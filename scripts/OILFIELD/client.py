"""
OILFIELD MQTT Client
====================
Escucha telemetría de dispositivos IoT de campo petrolero y la guarda en BD.

Sub-topics y tipos de dispositivo
──────────────────────────────────
  jhpAI/OILFIELD/tank          → TankStation  + TankIoTReading
  jhpAI/OILFIELD/wellanalyzer  → WellAnalyzerStation + AnalyzerReading

Protocolo de intercambio (análogo a FAUNA)
──────────────────────────────────────────
  1. El dispositivo publica en el topic de DATOS con su MAC y sus mediciones.
  2. El servidor responde en  jhpAI/OILFIELD/settings/{mac}  con la config
     actual (intervalo de muestreo, etc.).
  3. Si el dispositivo no está registrado, el mensaje se ignora y se logea.

Formato payload – TankStation (topic: jhpAI/OILFIELD/tank)
────────────────────────────────────────────────────────────
  Payload mínimo (campos confirmados en dispositivo real):
  {
    "type": "tankData",
    "mac":  "40:22:D8:22:A4:78",
    "LV":   "1965.2",   // Level (cm) — string o número
    "vB":   "3.96"      // Voltage Battery (V) — string o número
  }

  Campos opcionales adicionales (cuando el hardware los soporte):
    "TypeConn"  → TypeConn       (WIFI | LTE | GPRS | RS485)  — también acepta "conn"
    "timestamp" → LocalTimestamp (ISO 8601, hora local del dispositivo)
    "T"         → Temperature    (°C)
    "WL"        → WaterLevel     (cm)
    "V"         → Volume         (bbl) — calculado en el dispositivo

  También acepta el formato de configuración:
  {
    "type": "tankSetting",
    "mac":  "AA:BB:CC:DD:EE:FF"
  }

Formato payload – WellAnalyzerStation (topic: jhpAI/OILFIELD/wellanalyzer)
────────────────────────────────────────────────────────────────────────────
  {
    "type": "wellData",
    "mac":  "AA:BB:CC:DD:EE:FF",
    "conn": "WIFI",
    "timestamp": "2026-08-24T10:30:00",
    "SPM":  5.2,
    "FL":   72.5,   // Fillage (%)
    "RT":   23.5,   // RunTime (h)
    "OP":   35.0,   // OilProduction  (bbl/d)
    "WP":   12.0,   // WaterProduction (bbl/d)
    "TQ":   1240.0, // Torque (ft-lb)
    "A":    18.5,   // Motor Current (A)
    "VB":   2.1,    // Vibration (mm/s)
    "T":    42.3,   // Temperature (°C)
    "DL":   380.0,  // DynamicLevel (m)
    "VE":   68.0,   // VolumetricEfficiency (%)
    "ST":   "producing",  // OperationalStatus
    "vB":   12.6    // Voltage Battery (V)
  }

Uso
───
    cd RopPumpWeb/
    source /ruta/venv/bin/activate
    python scripts/OILFIELD/client.py

    # Con broker alternativo:
    python scripts/OILFIELD/client.py --broker 192.168.1.10 --port 1883
"""

import json
import logging
import os
import random
from datetime import datetime, timezone

import psycopg2
import paho.mqtt.client as mqtt

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
log = logging.getLogger('oilfield.client')

# ── Paths / secrets ───────────────────────────────────────────────────────────
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

with open(os.path.join(_ROOT, 'secret.json')) as _f:
    _SECRET = json.load(_f)

# ── MQTT config ───────────────────────────────────────────────────────────────
BROKER_ADDRESS = 'broker.hivemq.com'
BROKER_PORT    = 1883
CLIENT_ID      = f'oilfield-{random.randint(0, 9999)}'

TOPIC_TANK_DATA        = 'jhpAI/OILFIELD/tank'
TOPIC_WELLANALYZER_DATA = 'jhpAI/OILFIELD/wellanalyzer'
TOPIC_SETTINGS_PUB     = 'jhpAI/OILFIELD/settings'   # + /{mac}

TOPIC_SUB = 'jhpAI/OILFIELD/#'

# ── DB helpers (psycopg2 directo, igual que FAUNA) ────────────────────────────

def _conn():
    return psycopg2.connect(
        host='localhost',
        user=_SECRET['USER'],
        password=_SECRET['PASSWORD'],
        database=_SECRET['DB_NAME'],
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


# ── Helpers de parseo ─────────────────────────────────────────────────────────

def _float(val):
    if val is None or str(val).strip() in ('', 'NULL', 'nan'):
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def _parse_ts(val: str | None) -> datetime | None:
    """Parsea ISO 8601 del dispositivo a datetime naive UTC-like."""
    if not val:
        return None
    for fmt in ('%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S'):
        try:
            return datetime.strptime(val, fmt)
        except ValueError:
            pass
    return None


# ═════════════════════════════════════════════════════════════════════════════
# TANK — handlers
# ═════════════════════════════════════════════════════════════════════════════

def _get_tank_station(mac: str):
    """Retorna (id, sampling_rate) o None si el dispositivo no está registrado."""
    rows = db_get(
        'SELECT "id", "SamplingRate" '
        'FROM "oilfield_tank_tankstation" '
        'WHERE "MacAddress" = %s',
        (mac,),
    )
    return rows[0] if rows else None


def _reply_tank_settings(client: mqtt.Client, mac: str, sampling_rate: int):
    """Publica la configuración del dispositivo en su topic de respuesta."""
    payload = json.dumps({'samplingRate': sampling_rate})
    topic   = f'{TOPIC_SETTINGS_PUB}/{mac}'
    client.publish(topic, payload, qos=1)
    log.info('[TANK] Config enviada → %s  samplingRate=%s', mac, sampling_rate)


def _get_tank_id_from_station(station_id: int):
    """Retorna el Tank_id asociado a la estación IoT, o None."""
    rows = db_get(
        'SELECT "Tank_id" FROM "oilfield_tank_tankstation" WHERE "id" = %s',
        (station_id,),
    )
    return rows[0][0] if rows else None


def _save_tank_reading(station_id: int, server_dt: datetime,
                        local_ts: datetime | None, conn: str | None, data: dict):
    """Inserta en oilfield_tank_tankiotreading con Source='iot'."""
    tank_id = _get_tank_id_from_station(station_id)
    # tank_id puede ser None si la estación no tiene tanque asignado — se guarda igual

    db_exec(
        '''
        INSERT INTO "oilfield_tank_tankiotreading"
            ("Station_id", "Tank_id", "Source", "TypeConn",
             "ReadingDate", "LocalTimestamp", "DateCreate",
             "Level", "Temperature", "WaterLevel", "Volume", "VoltageBattery",
             "Notes")
        VALUES (%s, %s, 'iot', %s,
                %s, %s, NOW(),
                %s, %s, %s, %s, %s,
                '')
        ''',
        (
            station_id,
            tank_id,
            conn,
            server_dt,                # ReadingDate = timestamp servidor
            local_ts,                 # LocalTimestamp = timestamp dispositivo
            _float(data.get('LV')),   # Level (cm)
            _float(data.get('T')),    # Temperature  — opcional
            _float(data.get('WL')),   # WaterLevel   — opcional
            _float(data.get('V')),    # Volume (bbl) — opcional
            _float(data.get('vB')),   # VoltageBattery
        ),
    )
    # Actualizar LastSeen + VoltageBattery en la estación
    db_exec(
        '''
        UPDATE "oilfield_tank_tankstation"
        SET "LastSeen" = %s,
            "VoltageBattery" = COALESCE(%s, "VoltageBattery")
        WHERE "id" = %s
        ''',
        (server_dt, _float(data.get('vB')), station_id),
    )


def _handle_tank_data(client: mqtt.Client, data: dict):
    mac = data.get('mac', '').strip().upper()
    if not mac:
        log.warning('[TANK] Mensaje sin campo "mac" — descartado.')
        return

    station = _get_tank_station(mac)
    if not station:
        log.warning('[TANK] MAC %s no registrada en TankStation — descartado.', mac)
        return

    station_id, sampling_rate = station
    server_dt  = datetime.now(timezone.utc).replace(tzinfo=None)
    local_ts   = _parse_ts(data.get('timestamp'))
    conn       = data.get('TypeConn') or data.get('conn') or None

    # Responder con config
    _reply_tank_settings(client, mac, sampling_rate)

    # Guardar lectura
    _save_tank_reading(station_id, server_dt, local_ts, conn, data)
    log.info('[TANK] %s → LV=%.1f cm  T=%s°C  WL=%s cm  V=%s bbl  vB=%s V',
             mac,
             _float(data.get('LV')) or 0,
             data.get('T'), data.get('WL'), data.get('V'), data.get('vB'))


def _handle_tank_setting(client: mqtt.Client, data: dict):
    mac = data.get('mac', '').strip().upper()
    if not mac:
        return
    station = _get_tank_station(mac)
    if station:
        _reply_tank_settings(client, mac, station[1])
    else:
        log.warning('[TANK] tankSetting: MAC %s no registrada.', mac)


# ═════════════════════════════════════════════════════════════════════════════
# WELL ANALYZER — handlers
# ═════════════════════════════════════════════════════════════════════════════

def _get_well_station(mac: str):
    """Retorna (id, sampling_rate) o None."""
    rows = db_get(
        'SELECT "id", "SamplingRate" '
        'FROM "oilfield_wellanalyzer_wellanalyzerstation" '
        'WHERE "MacAddress" = %s',
        (mac,),
    )
    return rows[0] if rows else None


def _reply_well_settings(client: mqtt.Client, mac: str, sampling_rate: int):
    payload = json.dumps({'samplingRate': sampling_rate})
    topic   = f'{TOPIC_SETTINGS_PUB}/{mac}'
    client.publish(topic, payload, qos=1)
    log.info('[WELL] Config enviada → %s  samplingRate=%s', mac, sampling_rate)


def _save_well_reading(station_id: int, server_dt: datetime,
                        local_ts: datetime | None, conn: str | None, data: dict):
    op_status = data.get('ST', 'producing') or 'producing'
    db_exec(
        '''
        INSERT INTO "oilfield_wellanalyzer_analyzerreading"
            ("Station_id", "DateCreate", "LocalTimestamp", "TypeConn",
             "SPM", "Fillage", "RunTime", "OilProduction", "WaterProduction",
             "Torque", "MotorCurrent", "Vibration", "Temperature",
             "DynamicLevel", "VolumetricEfficiency",
             "OperationalStatus", "VoltageBattery")
        VALUES (%s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s,
                %s, %s)
        ''',
        (
            station_id,
            server_dt,
            local_ts,
            conn,
            _float(data.get('SPM')),
            _float(data.get('FL')),   # Fillage
            _float(data.get('RT')),   # RunTime
            _float(data.get('OP')),   # OilProduction
            _float(data.get('WP')),   # WaterProduction
            _float(data.get('TQ')),   # Torque
            _float(data.get('A')),    # MotorCurrent
            _float(data.get('VB')),   # Vibration
            _float(data.get('T')),    # Temperature
            _float(data.get('DL')),   # DynamicLevel
            _float(data.get('VE')),   # VolumetricEfficiency
            op_status,
            _float(data.get('vB')),   # VoltageBattery
        ),
    )
    # Actualizar estado en tiempo real de la estación
    db_exec(
        '''
        UPDATE "oilfield_wellanalyzer_wellanalyzerstation"
        SET "LastSeen"          = %s,
            "OperationalStatus" = %s,
            "VoltageBattery"    = COALESCE(%s, "VoltageBattery")
        WHERE "id" = %s
        ''',
        (server_dt, op_status, _float(data.get('vB')), station_id),
    )


def _handle_well_data(client: mqtt.Client, data: dict):
    mac = data.get('mac', '').strip().upper()
    if not mac:
        log.warning('[WELL] Mensaje sin campo "mac" — descartado.')
        return

    station = _get_well_station(mac)
    if not station:
        log.warning('[WELL] MAC %s no registrada en WellAnalyzerStation — descartado.', mac)
        return

    station_id, sampling_rate = station
    server_dt  = datetime.now(timezone.utc).replace(tzinfo=None)
    local_ts   = _parse_ts(data.get('timestamp'))
    conn       = data.get('conn', '')

    _reply_well_settings(client, mac, sampling_rate)
    _save_well_reading(station_id, server_dt, local_ts, conn, data)
    log.info('[WELL] %s → SPM=%s  FL=%s%%  OP=%s bbl/d  ST=%s',
             mac, data.get('SPM'), data.get('FL'), data.get('OP'), data.get('ST'))


def _handle_well_setting(client: mqtt.Client, data: dict):
    mac = data.get('mac', '').strip().upper()
    if not mac:
        return
    station = _get_well_station(mac)
    if station:
        _reply_well_settings(client, mac, station[1])
    else:
        log.warning('[WELL] wellSetting: MAC %s no registrada.', mac)


# ═════════════════════════════════════════════════════════════════════════════
# Router de mensajes MQTT
# ═════════════════════════════════════════════════════════════════════════════

_HANDLERS = {
    # tank
    'tankData':    _handle_tank_data,
    'tankSetting': _handle_tank_setting,
    # well analyzer
    'wellData':    _handle_well_data,
    'wellSetting': _handle_well_setting,
}


def _route_message(client: mqtt.Client, topic: str, payload_str: str):
    """Parsea el JSON y despacha al handler correspondiente por 'type'."""
    try:
        data = json.loads(payload_str)
    except json.JSONDecodeError as exc:
        log.warning('JSON inválido en topic %s: %s', topic, exc)
        return

    # Inferir tipo desde topic si no viene en el payload
    msg_type = data.get('type', '')
    if not msg_type:
        if topic == TOPIC_TANK_DATA:
            msg_type = 'tankData'
        elif topic == TOPIC_WELLANALYZER_DATA:
            msg_type = 'wellData'

    handler = _HANDLERS.get(msg_type)
    if handler:
        try:
            handler(client, data)
        except Exception as exc:
            log.exception('[%s] Error procesando mensaje: %s', msg_type, exc)
    else:
        log.debug('Tipo de mensaje desconocido "%s" en topic %s — ignorado.', msg_type, topic)


# ═════════════════════════════════════════════════════════════════════════════
# Callbacks MQTT
# ═════════════════════════════════════════════════════════════════════════════

def _on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        client.subscribe(TOPIC_SUB, qos=1)
        log.info('Conectado al broker. Suscrito a: %s', TOPIC_SUB)
    else:
        log.error('Error de conexión MQTT, código: %s', rc)


def _on_disconnect(client, userdata, rc, properties=None, reason_code=None):
    log.warning('Desconectado del broker (rc=%s). Reconectando...', rc)


def _on_message(client, userdata, msg):
    topic   = msg.topic
    payload = msg.payload.decode('utf-8', errors='replace')
    log.debug('MQTT  topic=%s  payload=%s', topic, payload[:200])
    _route_message(client, topic, payload)


# ═════════════════════════════════════════════════════════════════════════════
# Main
# ═════════════════════════════════════════════════════════════════════════════

def main():
    import argparse
    parser = argparse.ArgumentParser(description='OILFIELD MQTT Client')
    parser.add_argument('--broker', default=BROKER_ADDRESS)
    parser.add_argument('--port',   type=int, default=BROKER_PORT)
    args = parser.parse_args()

    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id=CLIENT_ID,
    )
    client.on_connect    = _on_connect
    client.on_disconnect = _on_disconnect
    client.on_message    = _on_message

    log.info('Conectando a %s:%d …', args.broker, args.port)
    client.connect(args.broker, args.port, keepalive=60)
    client.loop_forever()


if __name__ == '__main__':
    main()
