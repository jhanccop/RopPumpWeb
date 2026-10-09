"""
HIDROMET MQTT Client
====================
Recibe lecturas de las estaciones hidrometeorológicas y las guarda en
"hidromet_hydroreading". Responde a cada estación con su configuración.

Subscribed topic : jhpAI/HIDROMET/data
Published topic  : jhpAI/HIDROMET/settings/{MAC en mayúsculas, sin ":"}   ej. .../settings/4022D822A478

Message types (JSON field "type"):
  hydroStationSetting → solo responde con la configuración (p. ej. al encender el equipo)
  hydroStationData    → responde con la configuración y guarda la lectura

El MAC se compara sin distinguir mayúsculas ni separadores (":" "-"), y la respuesta se
publica siempre en el topic con el MAC normalizado. MAC no registrado → no hay respuesta.

Inbound payload (type = "hydroStationSetting"):
  {"type":"hydroStationSetting","mac":"AA:BB:CC:DD:EE:FF"}

Inbound payload (type = "hydroStationData"):
  {"type":"hydroStationData","mac":"AA:BB:CC:DD:EE:FF",
   "conn":"LTE","timestamp":"2026-10-02T14:53:28",
   "T":21.3,"H":87.7,"WD":106.5,"WV":1.10,"PR":0.4,"RAD":260,
   "LV":1.235,"PH":7.42,"TW":14.8,"vB":3.92}

  Campos:
    conn      → TypeConn          (WIFI | LTE)
    timestamp → LocalTimestamp    (hora Lima del dispositivo, ISO 8601)
    T         → Temperature       (°C, ambiente)
    H         → Humidity          (%)
    WD        → WindDirection     (°, 0–360)
    WV        → WindSpeed         (m/s)
    PR        → Precipitation     (mm acumulados en el intervalo)
    RAD       → SolarRadiation    (W/m²)
    LV        → RawDistance       (m, distancia del sensor —montado arriba— a la superficie del agua)
                → WaterLevel        (m, altura del flujo = LevelTare de la estación − LV)
    PH        → WaterPH           (0–14)
    TW        → WaterTemperature  (°C)
    vB        → VoltageBattery    (V)
    DateCreate se asigna con la hora del servidor al recibir el mensaje.

  Las columnas son timestamptz: ambas fechas se insertan con zona horaria explícita
  para no depender de la zona de la sesión de PostgreSQL (Django lee en UTC).

Reply payload (configuración registrada en la BD para esa estación):
  {"status":true,"timesleep":15,
   "A_TH":true,"A_WS":false,"A_RD":false,"A_PR":true,"A_LV":true,"A_PH":true,"A_TW":true,
   "tare":5.765,"levelWarning":3.0,"levelCritical":4.57,
   "serverTime":"2026-10-02T14:53:30"}

    status     → Status == "Active"
    timesleep  → TimeSleep en minutos
    A_*        → sensores habilitados (TH temp/humedad, WS viento, RD radiación, PR precipitación,
                 LV nivel, PH pH, TW temperatura de agua)
    tare, levelWarning, levelCritical → m (null si no están configurados)
    serverTime → hora Lima del servidor, para sincronizar el RTC del equipo
"""

import json
import os
import queue
import random
import threading
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import psycopg2
import paho.mqtt.client as mqtt

# ── MQTT ──────────────────────────────────────────────────────
BROKER_ADDRESS = "broker.hivemq.com"
BROKER_PORT    = 1883
CLIENT_ID      = f"hidromet-{random.randint(0, 9999)}"
USERNAME       = "jhanccop"
PASSWORD       = "jhanccop1"

DEVICE_TZ = ZoneInfo("America/Lima")   # zona horaria del reloj de las estaciones

TOPIC_SUB  = "jhpAI/HIDROMET/#"
TOPIC_DATA = "jhpAI/HIDROMET/data"
TOPIC_PUB  = "jhpAI/HIDROMET/settings"

# ── Paths / secrets ───────────────────────────────────────────
# scripts/HIDROMET/client.py → scripts/ → project root (RopPumpWeb/)
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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


# ── Misc helpers ──────────────────────────────────────────────
def _float(val):
    """Return float or None for missing/NaN values."""
    if val is None or str(val).strip() in ("", "NULL", "nan"):
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def _timesleep_int(val):
    """'5m' → 5, '1h' → 60 (minutos)."""
    if not val:
        return 15
    val = str(val).strip()
    if val.endswith("h"):
        return int(val[:-1]) * 60
    if val.endswith("m"):
        return int(val[:-1])
    return int(val)


def _parse_device_timestamp(raw):
    """Parse ISO 8601 timestamp (hora Lima) sent by the device; returns aware datetime or None."""
    if not raw:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M"):
        try:
            return datetime.strptime(raw, fmt).replace(tzinfo=DEVICE_TZ)
        except ValueError:
            continue
    return None


# ── Handlers ──────────────────────────────────────────────────
_STATION_FIELDS = (
    "id", "Status", "TimeSleep",
    "HasTempHumidity", "HasWind", "HasSolarRadiation", "HasPrecipitation",
    "HasWaterLevel", "HasWaterPH", "HasWaterTemp",
    "LevelTare", "LevelWarning", "LevelCritical",
)


def _norm_mac(mac):
    """'aa:bb-cc dd:ee:ff' → 'AABBCCDDEEFF'."""
    return "".join(ch for ch in str(mac or "").upper() if ch.isalnum())


def _get_station(mac):
    """Configuración registrada de la estación con ese MAC (dict), o None."""
    cols = ",".join(f'"{f}"' for f in _STATION_FIELDS)
    rows = db_get(
        f"""SELECT {cols} FROM "hidromet_hydrostation"
            WHERE UPPER(REGEXP_REPLACE(COALESCE("MacAddress", ''), '[^A-Za-z0-9]', '', 'g')) = %s""",
        (_norm_mac(mac),),
    )
    if not rows:
        return None
    if len(rows) > 1:
        print(f"[hm] WARNING: {len(rows)} estaciones con MAC {mac}; se usa id={rows[0][0]}")
    return dict(zip(_STATION_FIELDS, rows[0]))


def _settings_payload(st):
    return {
        "status":        st["Status"] == "Active",
        "timesleep":     _timesleep_int(st["TimeSleep"]),
        "A_TH":          bool(st["HasTempHumidity"]),
        "A_WS":          bool(st["HasWind"]),
        "A_RD":          bool(st["HasSolarRadiation"]),
        "A_PR":          bool(st["HasPrecipitation"]),
        "A_LV":          bool(st["HasWaterLevel"]),
        "A_PH":          bool(st["HasWaterPH"]),
        "A_TW":          bool(st["HasWaterTemp"]),
        "tare":          st["LevelTare"],
        "levelWarning":  st["LevelWarning"],
        "levelCritical": st["LevelCritical"],
        # Hora Lima (no la del servidor, que en producción está en UTC): el equipo
        # sincroniza su RTC con esto y envía "timestamp" en hora Lima.
        "serverTime":    datetime.now(DEVICE_TZ).strftime("%Y-%m-%dT%H:%M:%S"),
    }


def _reply(client, mac, st):
    """Publica la configuración registrada en settings/{MAC normalizado}."""
    topic = f"{TOPIC_PUB}/{_norm_mac(mac)}"
    payload = json.dumps(_settings_payload(st))
    info = client.publish(topic, payload, qos=1)
    print(f"[hm-reply] → {topic}  rc={info.rc}  {payload}")
    return topic, payload


def _handle_settings(client, data):
    mac = data.get("mac", "")
    st = _get_station(mac)
    if st is None:
        print(f"[hm-settings] unknown MAC: {mac}")
        return
    _reply(client, mac, st)


def _handle_data(client, data):
    mac = data.get("mac", "")
    st = _get_station(mac)
    if st is None:
        print(f"[hm-data] unknown MAC: {mac}")
        return

    # 1. Responder primero para no bloquear al equipo
    _reply(client, mac, st)
    station_id, tare = st["id"], st["LevelTare"]

    raw_distance = _float(data.get("LV"))
    water_level  = (round(tare - raw_distance, 4)
                    if tare is not None and raw_distance is not None else None)

    server_dt = datetime.now(timezone.utc)
    local_ts  = _parse_device_timestamp(data.get("timestamp"))
    db_exec(
        """INSERT INTO "hidromet_hydroreading"
           ("Station_id","DateCreate","LocalTimestamp","TypeConn",
            "Temperature","Humidity","WindDirection","WindSpeed",
            "Precipitation","SolarRadiation",
            "RawDistance","WaterLevel","WaterPH","WaterTemperature","VoltageBattery")
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (
            station_id, server_dt, local_ts, data.get("conn"),
            _float(data.get("T")),
            _float(data.get("H")),
            _float(data.get("WD")),
            _float(data.get("WV")),
            _float(data.get("PR")),
            _float(data.get("RAD")),
            raw_distance,
            water_level,
            _float(data.get("PH")),
            _float(data.get("TW")),
            _float(data.get("vB")),
        ),
    )
    print(
        f"[hm-data] saved  station={station_id}  device={local_ts}"
        f"  LV={raw_distance}  tara={tare}  flujo={water_level}  PH={data.get('PH')}  TW={data.get('TW')}  T={data.get('T')}"
    )


# ── Message queue — decouples network thread from processing ──
_queue = queue.Queue()


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
    if topic != TOPIC_DATA:
        print(f"[warn] unhandled topic: {topic!r}")
        return

    data = json.loads(payload.decode("utf-8"))
    msg_type = data.get("type", "")
    print(f"[{datetime.now():%H:%M:%S}] type={msg_type!r}")
    handler = {
        "hydroStationSetting": _handle_settings,
        "hydroStationData":    _handle_data,
    }.get(msg_type)
    if handler:
        handler(client, data)
    else:
        print(f"[warn] unhandled type: {msg_type!r}")


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
    # paho-mqtt ≥2.0 requires callback_api_version; 1.x does not have it
    if hasattr(mqtt, "CallbackAPIVersion"):
        client = mqtt.Client(
            client_id=CLIENT_ID,
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        )
    else:
        client = mqtt.Client(client_id=CLIENT_ID)
    client.username_pw_set(USERNAME, PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER_ADDRESS, BROKER_PORT, keepalive=60)

    threading.Thread(target=_worker, args=(client,), daemon=True).start()

    print(f"[HIDROMET client] connecting to {BROKER_ADDRESS}:{BROKER_PORT} ...")
    client.loop_forever()
