"""
FAUNA MQTT Client
=================
Handles messages from WeatherStation and CameraStation devices.

Subscribed topic : fauna/data
Published topic  : fauna/settings/{mac}

Message types (JSON field "type"):
  weatherStationSetting  → responds with device config
  weatherStationData     → stores WeatherReading
  cameraStationSetting   → responds with device config
  cameraCapture          → stores CameraCapture (with optional image)

Inbound payloads
────────────────
weatherStationSetting:
  {"type":"weatherStationSetting","mac":"AA:BB:CC:DD:EE:FF"}

weatherStationData:
  {"type":"weatherStationData","mac":"AA:BB:CC:DD:EE:FF",
   "T":25.3,"H":60.1,"WV":2.5,"WD":180,"RA":850,"P":1.2}

cameraStationSetting:
  {"type":"cameraStationSetting","mac":"AA:BB:CC:DD:EE:FF"}

cameraCapture:
  {"type":"cameraCapture","mac":"AA:BB:CC:DD:EE:FF",
   "datetime":"2026-04-18T10:30:00",
   "T":22.5,"H":55.0,"B":3.8,
   "species":"Plutella xylostella","count":2,
   "image":"<base64 jpg>","notes":""}
"""

import json
import os
import queue
import random
import threading
from datetime import datetime, time
from zoneinfo import ZoneInfo

import psycopg2
import paho.mqtt.client as mqtt

# ── MQTT ──────────────────────────────────────────────────────
BROKER_ADDRESS = "broker.hivemq.com"#"24.199.125.52"
BROKER_PORT    = 1883
CLIENT_ID      = f"fauna-{random.randint(0, 9999)}"
USERNAME       = "jhanccop"
PASSWORD       = "jhanccop1"

TOPIC_SUB   = "jhpAI/FAUNA/#"
TOPIC_DATA  = "jhpAI/FAUNA/data"          # JSON messages
TOPIC_IMAGE = "jhpAI/FAUNA/trapViewImage"  # binary JPEG → + /{mac}
TOPIC_PUB   = "jhpAI/FAUNA/settings"

# ── Paths / secrets ───────────────────────────────────────────
# scripts/FAUNA/client.py → scripts/ → project root (RopPumpWeb/)
_ROOT  = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_MEDIA = os.path.join(_ROOT, "media")

with open(os.path.join(_ROOT, "secret.json")) as _f:
    _SECRET = json.load(_f)


# ── DB helpers ────────────────────────────────────────────────
def _conn():
    return psycopg2.connect(
        host="localhost",
        user=_SECRET["USER"],
        password=_SECRET["PASSWORD"],
        database=_SECRET["DB_NAME"],
    )


def db_get(sql, params=None):
    con = _conn()
    try:
        with con.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        con.close()


def db_exec(sql, params=None):
    con = _conn()
    try:
        with con.cursor() as cur:
            cur.execute(sql, params)
        con.commit()
    finally:
        con.close()


def db_exec_returning(sql, params=None):
    """Execute INSERT ... RETURNING and return the result rows."""
    con = _conn()
    try:
        with con.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
        con.commit()
        return rows
    finally:
        con.close()


# ── Misc helpers ──────────────────────────────────────────────
def _float(val):
    """Return float or None for missing/NaN values."""
    if val is None or str(val).strip() in ("", "NULL", "nan"):
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def _species_name(class_id: int) -> str:
    """Look up the configured species name for a class ID, fallback to 'class_N'."""
    rows = db_get(
        'SELECT "Name" FROM "camera_specieslabel" WHERE "ClassId" = %s',
        (class_id,),
    )
    return rows[0][0] if rows else f"class_{class_id}"


_TIMESLEEP_MAP = {"5m": 5, "30m": 30, "1h": 60}

def _timesleep_int(val: str) -> int:
    return _TIMESLEEP_MAP.get(str(val), 30)


# Pending sensor metadata keyed by MAC (populated by cameraData)
_pending: dict = {}

# Partial image bytes accumulator keyed by MAC (chunks until JPEG EOI FF D9)
_img_buf: dict[str, bytearray] = {}

# Timeout timers: if no new chunk arrives within IMG_TIMEOUT seconds, flush buffer
_img_timers: dict[str, threading.Timer] = {}
IMG_TIMEOUT = 2.0  # seconds to wait for additional chunks before forcing save

_JPEG_SOI = b'\xff\xd8'
_JPEG_EOI = b'\xff\xd9'


def _flush_img_buf(mac: str, client):
    """Called by timer: save whatever bytes are in the buffer then clear it."""
    _img_timers.pop(mac, None)
    buf = _img_buf.pop(mac, None)
    if buf and mac in _pending:
        complete = bytes(buf).endswith(_JPEG_EOI)
        print(f"[image] timeout flush  mac={mac}  {len(buf)}B  EOI={'✓' if complete else '✗ (truncated)'}")
        _handle_cam_capture(mac, bytes(buf), client)


def _reset_img_timer(mac: str, client):
    """Cancel any running flush timer for this MAC and start a fresh one."""
    old = _img_timers.pop(mac, None)
    if old:
        old.cancel()
    t = threading.Timer(IMG_TIMEOUT, _flush_img_buf, args=(mac, client))
    t.daemon = True
    t.start()
    _img_timers[mac] = t


def _cancel_img_timer(mac: str):
    t = _img_timers.pop(mac, None)
    if t:
        t.cancel()


def _save_image(raw_bytes: bytes, filename: str) -> str | None:
    """Write raw JPEG bytes to media dir, return relative path."""
    if not raw_bytes:
        return None
    try:
        now = datetime.now()
        rel_dir = os.path.join("camera_captures", str(now.year), f"{now.month:02d}")
        abs_dir = os.path.join(_MEDIA, rel_dir)
        os.makedirs(abs_dir, exist_ok=True)
        with open(os.path.join(abs_dir, filename), "wb") as f:
            f.write(raw_bytes)
        return os.path.join(rel_dir, filename)
    except Exception as e:
        print(f"[image] save error: {e}")
        return None


# ── Weather Station handlers ──────────────────────────────────
def _handle_ws_data(client, data):
    """Store a WeatherReading, then reply with station config."""
    mac = data.get("mac", "")
    rows = db_get(
        """SELECT id,"Status","TimeSleep",
                  "HasTempHumidity","HasWind","HasSolarRadiation","HasPrecipitation"
           FROM "weatherStation_weatherstation"
           WHERE "MacAddress" = %s""",
        (mac,),
    )
    if not rows:
        print(f"[ws-data] unknown MAC: {mac}")
        return

    station_id, status, timesleep, a_th, a_ws, a_rd, a_pr = rows[0]
    dt = datetime.now()

    db_exec(
        """INSERT INTO "weatherStation_weatherreading"
           ("Station_id","DateCreate",
            "Temperature","Humidity","SolarRadiation",
            "Precipitation","WindSpeed","WindDirection","VoltageBattery")
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (
            station_id, dt,
            _float(data.get("T")),
            _float(data.get("H")),
            _float(data.get("RS")),
            _float(data.get("P")),
            _float(data.get("WV")),
            _float(data.get("WD")),
            _float(data.get("vB")),
        ),
    )
    print(f"[ws-data] station={station_id}  T={data.get('T')}  H={data.get('H')}  vB={data.get('vB')}")

    payload = json.dumps({
        "status":   status == "Active",
        "timesleep": _timesleep_int(timesleep),
        "A_TH":     bool(a_th),
        "A_WS":     bool(a_ws),
        "A_RD":     bool(a_rd),
        "A_PR":     bool(a_pr),
    })
    mac_norm = mac.replace(":", "")
    client.publish(f"{TOPIC_PUB}/{mac_norm}", payload)
    print(f"[ws-data] → {mac_norm}  {payload}")


# ── Camera Station handlers ───────────────────────────────────
def _cam_reply(client, mac: str):
    """Query station config and publish settings reply to the device."""
    rows = db_get(
        """SELECT "HasTempHumidity","TimeSleep","TimeSleepC","Sensitivity","TurnOnTime","TurnOffTime"
           FROM "camera_camerastation" WHERE "MacAddress" = %s""",
        (mac,),
    )
    if not rows:
        print(f"[cam-reply] unknown MAC: {mac}")
        return
    a_th, tsleep, tsleepc, sensitivity, ton, toff = rows[0]

    # Obtener hora actual en zona Perú
    peru_tz = ZoneInfo('America/Lima')
    now_peru = datetime.now(peru_tz)
    
    # Función para convertir a time si es necesario
    def to_time(value):
        if value is None:
            return None
        if isinstance(value, time):
            return value
        if isinstance(value, str):
            # Intentar diferentes formatos
            for fmt in ['%H:%M:%S', '%H:%M']:
                try:
                    return datetime.strptime(value, fmt).time()
                except ValueError:
                    continue
            raise ValueError(f"Invalid time format: {value}")
        return value
    
    ton_time = to_time(ton)
    toff_time = to_time(toff)
    
    if ton_time and toff_time:
        now_time = now_peru.time()
        
        # Comparar usando hora Perú
        if ton_time <= toff_time:
            active = ton_time <= now_time <= toff_time
        else:  # cruza la medianoche
            active = now_time >= ton_time or now_time <= toff_time
    else:
        active = True

    payload = json.dumps({
        "status":    active,
        "A_TH":      bool(a_th),
        "timesleep": _timesleep_int(tsleep),
        "timesleepC": int(tsleepc) if tsleepc is not None else 30,
        "sen":       round(float(sensitivity) if sensitivity is not None else 0.6, 2),
    })
    mac_norm = mac.replace(":", "")
    client.publish(f"{TOPIC_PUB}/{mac_norm}", payload)
    print(f"[cam-reply] → {mac_norm}  {payload}")
    print(f"[cam-reply] debug - Hora Perú: {now_peru.strftime('%H:%M:%S')}, On: {ton_time}, Off: {toff_time}, Active: {active}")

def _handle_cam_data(client, data):
    """Cache sensor data in _pending, flush any stale image buffer, reply with config."""
    mac = data.get("mac", "")

    # If a previous image buffer was never completed, save whatever arrived
    if mac in _img_buf and len(_img_buf[mac]) > 0:
        _cancel_img_timer(mac)
        print(f"[cam-data] flushing stale buffer for {mac}  {len(_img_buf[mac])}B")
        if mac in _pending:
            _handle_cam_capture(mac, bytes(_img_buf[mac]), client)
        del _img_buf[mac]

    _pending[mac] = {
        "imageName":   data.get("imageName", f"{mac.replace(':', '')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"),
        "temperature": _float(data.get("temperature")),
        "humidity":    _float(data.get("humidity")),
        "battery":     _float(data.get("battery")),
        "objectCount": int(data.get("objectCount", 0)),
        "detected":    bool(data.get("detected", False)),
        "targetClass": int(data.get("targetClass", 0)),
    }
    print(f"[cam-data] pending  mac={mac}  img={_pending[mac]['imageName']}"
          f"  T={_pending[mac]['temperature']}  H={_pending[mac]['humidity']}"
          f"  detected={_pending[mac]['detected']}")
    #_cam_reply(client, mac)


def _handle_cam_capture(mac: str, raw_bytes: bytes, client=None):
    """Save binary JPEG and insert CameraCapture using pending sensor data."""
    rows = db_get(
        'SELECT id FROM "camera_camerastation" WHERE "MacAddress" = %s',
        (mac,),
    )
    if not rows:
        print(f"[cam-capture] unknown MAC: {mac}")
        return

    station_id = rows[0][0]
    meta     = _pending.pop(mac, {})
    filename = meta.get("imageName", f"{mac.replace(':', '')}_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}.jpg")

    img_path = _save_image(raw_bytes, filename)
    if not img_path:
        print(f"[cam-capture] image save failed for MAC: {mac}")
        # NO enviar respuesta si la imagen no se guardó
        return

    detected   = meta.get("detected", False)
    obj_count  = int(meta.get("objectCount", 0))
    target_cls = int(meta.get("targetClass", 0))

    rows2 = db_exec_returning(
        """INSERT INTO "camera_cameracapture"
               ("Station_id","DateCapture","Image",
                "Temperature","Humidity","VoltageBattery","Notes")
           VALUES (%s,%s,%s,%s,%s,%s,%s)
           RETURNING id""",
        (
            station_id, datetime.now(), img_path,
            meta.get("temperature"),
            meta.get("humidity"),
            meta.get("battery"),
            "",
        ),
    )
    if not rows2:
        print(f"[cam-capture] INSERT failed for station={station_id}")
        return

    capture_id = rows2[0][0]

    if detected and obj_count > 0:
        species_label = _species_name(target_cls)
        db_exec(
            """INSERT INTO "camera_capturedetection"
               ("Capture_id","Species","Count")
               VALUES (%s,%s,%s)""",
            (capture_id, species_label, obj_count),
        )
        print(f"[cam-capture] station={station_id}  id={capture_id}"
              f"  species={species_label}  count={obj_count}  img={filename}")
    else:
        print(f"[cam-capture] station={station_id}  id={capture_id}  no detection  img={filename}")

    # SOLO enviar respuesta si el cliente MQTT está conectado Y tenemos una imagen válida
    if client and img_path:
        print(f"[cam-reply] → {mac}  enviando configuración")
        _cam_reply(client, mac)


# ── Message queue — decouples network thread from processing ──
_queue: queue.Queue = queue.Queue()


def _worker(client):
    """Background thread: dequeues and processes messages one at a time."""
    while True:
        topic, payload = _queue.get()
        try:
            _process(client, topic, payload)
        except Exception as e:
            print(f"[error] worker: {e}")
        finally:
            _queue.task_done()

def _process(client, topic, payload):
    # Ignore our own outbound settings messages
    if topic.startswith(TOPIC_PUB):
        return

    # ── Binary image ──────────────────────────────────────────────────────────
    if topic == TOPIC_IMAGE:
        if not _pending:
            print(f"[{datetime.now():%H:%M:%S}] trapViewImage  no pending cameraData — dropped")
            return
        mac = next(iter(_pending))
        
        buf = _img_buf.setdefault(mac, bytearray())
        buf.extend(payload)
        
        starts_ok = buf[:2] == _JPEG_SOI
        ends_ok   = buf[-2:] == _JPEG_EOI
        
        print(f"[{datetime.now():%H:%M:%S}] trapViewImage  mac={mac}"
            f"  chunk={len(payload)}B  total={len(buf)}B"
            f"  SOI={'✓' if starts_ok else '✗'}  EOI={'✓' if ends_ok else '…'}")
        
        # Si está completo O si el chunk actual ya contiene EOI (caso mensaje único)
        if ends_ok or (payload[-2:] == _JPEG_EOI and len(buf) == len(payload)):
            _cancel_img_timer(mac)
            complete = bytes(buf)
            del _img_buf[mac]
            print(f"[image] imagen completa recibida ({len(complete)} bytes)")
            _handle_cam_capture(mac, complete, client)
        else:
            # Solo esperar si el buffer no tiene EOI
            _reset_img_timer(mac, client)
        return

    # ── JSON data ─────────────────────────────────────────────────────────────
    if topic == TOPIC_DATA:
        data = json.loads(payload.decode("utf-8"))
        msg_type = data.get("type", "")
        print(f"[{datetime.now():%H:%M:%S}] type={msg_type!r}")

        dispatch = {
            "weatherStationData": lambda: _handle_ws_data(client, data),
            "cameraData":         lambda: _handle_cam_data(client, data),
        }
        handler = dispatch.get(msg_type)
        if handler:
            handler()
        else:
            print(f"[warn] unhandled type: {msg_type!r}")
        return

    print(f"[warn] unhandled topic: {topic!r}")


# ── MQTT callbacks ────────────────────────────────────────────
def on_connect(client, _userdata, _flags, rc, _properties=None):
    print(f"[MQTT] connected rc={rc}")
    client.subscribe(TOPIC_SUB)
    print(f"[MQTT] subscribed → {TOPIC_SUB}")


def on_message(_client, _userdata, message):
    """Enqueue immediately — never blocks the MQTT network thread."""
    _queue.put((message.topic, message.payload))


# ── Entry point ───────────────────────────────────────────────
if __name__ == "__main__":
    client = mqtt.Client(
        client_id=CLIENT_ID,
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    )
    client.username_pw_set(USERNAME, PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER_ADDRESS, BROKER_PORT, keepalive=60)

    threading.Thread(target=_worker, args=(client,), daemon=True).start()

    print(f"[FAUNA client] connecting to {BROKER_ADDRESS}:{BROKER_PORT} ...")
    client.loop_forever()
