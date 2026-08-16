"""
SEGURIDAD MQTT Client
=====================
Escucha mensajes de dispositivos de seguridad de ambiente controlado
y los guarda en la base de datos (modelos SecurityDevice, Sensor, EventLog).

Uso
---
    python client.py [--settings <django_settings_module>]

    Por defecto usa: RopPumpWeb.settings.local
    Puede sobreescribirse con la variable de entorno DJANGO_SETTINGS_MODULE.

Configuración del broker
------------------------
    El broker, puerto y topic se configuran por dispositivo en la base de datos
    (campos MqttBroker, MqttPort, MqttTopic de SecurityDevice).
    El script carga todos los dispositivos activos al iniciar y suscribe
    cada uno a su topic.  También admite un broker/topic global por línea
    de comandos (opción --broker / --port / --topic) para entornos simples.

Formato del mensaje MQTT (JSON)
--------------------------------
    Topic: <MqttTopic configurado>  (ej. "seguridad/maestro01/critico")
    {
      "dispositivo": "MAESTRO-01",     # nombre del dispositivo en BD
      "sensor":      "Puerta tablero", # nombre del sensor (campo Sensor.Name)
      "detalle":     "activo",         # descripción del evento
      "categoria":   "critico",        # critico | alto | informativo
      "canal":       "wifi"            # wifi | gprs
    }

Lógica de parseo del campo "detalle"
--------------------------------------
  Estado del sensor:
    - contiene "activo"      → Estado='activo'
    - contiene "normalizado" → Estado='normal'
    - cualquier otro         → Estado='normal'

  Origen (maestro / esclavo):
    - detalle contiene "(esclavo)" → Origin='esclavo'
    - en caso contrario            → Origin='maestro'

  También se detecta la categoría desde el sub-topic cuando el topic
  usa wildcards (seguridad/+/#): último segmento del topic = categoria.

Ejemplos de detalle por categoría
-----------------------------------
  CRÍTICO:
    "activo" / "normalizado"
    "activo (esclavo)" / "normalizado (esclavo)"
    "enlace perdido (timeout RS485)" / "enlace restablecido"
    "<N> intentos de acceso RECHAZADOS - dni:<dni>"

  INFORMATIVO:
    "ACCESO AUTORIZADO - usuario:<nombre>"
    "ACCESO DENEGADO - dni:<dni>"
    "FIN DE ACCESO (PERIODO DE BYPASS) - usuario:<nombre>"
"""

import argparse
import json
import logging
import os
import sys
import time as _time
from datetime import datetime

import django

# ── Django setup ──────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RopPumpWeb.settings.local')

def _setup_django(settings_module: str | None = None):
    if settings_module:
        os.environ['DJANGO_SETTINGS_MODULE'] = settings_module
    django.setup()

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
log = logging.getLogger('seguridad.client')

# ── MQTT import (paho-mqtt requerido) ─────────────────────────────────────────
try:
    import paho.mqtt.client as mqtt
except ImportError:
    log.error('paho-mqtt no instalado. Ejecuta: pip install paho-mqtt')
    sys.exit(1)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers de parseo
# ─────────────────────────────────────────────────────────────────────────────

def _parse_estado(detalle: str) -> str:
    """Determina el estado del sensor a partir del campo 'detalle'."""
    d = detalle.lower()
    if 'activo' in d:
        return 'activo'
    if 'normalizado' in d or 'restablecido' in d or 'autorizado' in d:
        return 'normal'
    # Eventos de acceso denegado / bypass / info → 'activo' como disparador
    if 'denegado' in d or 'rechazado' in d or 'intentos' in d or 'perdido' in d:
        return 'activo'
    if 'fin de acceso' in d:
        return 'normal'
    return 'normal'


def _parse_origin(detalle: str) -> str:
    """Determina el origen (maestro/esclavo) a partir del campo 'detalle'."""
    return 'esclavo' if '(esclavo)' in detalle.lower() else 'maestro'


def _categoria_from_topic(topic: str, payload_categoria: str) -> str:
    """
    Intenta extraer la categoría del último segmento del topic.
    Si el topic termina en critico/alto/informativo, eso tiene prioridad.
    De lo contrario usa el valor del payload.
    """
    VALID = {'critico', 'alto', 'informativo'}
    last = topic.rstrip('/').split('/')[-1].lower()
    if last in VALID:
        return last
    return payload_categoria.lower() if payload_categoria.lower() in VALID else 'informativo'


# ─────────────────────────────────────────────────────────────────────────────
# Procesamiento del mensaje
# ─────────────────────────────────────────────────────────────────────────────

def _process_message(topic: str, payload_str: str):
    """
    Parsea el payload JSON y guarda el evento en la base de datos.
    También actualiza Sensor.CurrentState y SecurityDevice.LastSeen.
    """
    from Apps.SEGURIDAD.models import SecurityDevice, Sensor, EventLog

    # ── Parsear JSON ──────────────────────────────────────────────────────────
    try:
        data = json.loads(payload_str)
    except json.JSONDecodeError as exc:
        log.warning('JSON inválido en topic %s: %s', topic, exc)
        return

    nombre_dispositivo = data.get('dispositivo', '').strip()
    sensor_name        = data.get('sensor', '').strip()
    detalle            = data.get('detalle', '').strip()
    categoria_raw      = data.get('categoria', 'informativo')
    canal              = data.get('canal', '')

    if not nombre_dispositivo:
        log.warning('Mensaje sin campo "dispositivo" — descartado. topic=%s', topic)
        return

    # ── Buscar dispositivo en BD ──────────────────────────────────────────────
    try:
        device = SecurityDevice.objects.get(Name=nombre_dispositivo)
    except SecurityDevice.DoesNotExist:
        log.warning('Dispositivo "%s" no registrado en BD — descartado.', nombre_dispositivo)
        return

    # ── Derivar campos ────────────────────────────────────────────────────────
    categoria = _categoria_from_topic(topic, categoria_raw)
    estado    = _parse_estado(detalle)
    origin    = _parse_origin(detalle)
    now       = datetime.utcnow()

    # ── Buscar sensor (por nombre) para obtener índice y estado configurado ───
    sensor_obj = None
    try:
        sensor_obj = Sensor.objects.get(Device=device, Name__iexact=sensor_name)
    except Sensor.DoesNotExist:
        # Intentar búsqueda flexible (sin tildes / mayúsculas)
        pass
    except Sensor.MultipleObjectsReturned:
        sensor_obj = Sensor.objects.filter(Device=device, Name__iexact=sensor_name).first()

    sensor_index = sensor_obj.SensorIndex if sensor_obj else None

    # ── Guardar EventLog ──────────────────────────────────────────────────────
    event = EventLog.objects.create(
        Device          = device,
        Origin          = origin,
        SensorIndex     = sensor_index,
        SensorName      = sensor_name or None,
        Estado          = estado,
        Category        = categoria,
        Canal           = canal or None,
        Notes           = detalle,
    )

    # ── Actualizar estado en tiempo real del sensor ───────────────────────────
    if sensor_obj:
        sensor_obj.CurrentState = estado
        sensor_obj.save(update_fields=['CurrentState'])

    # ── Actualizar LastSeen del dispositivo ───────────────────────────────────
    device.LastSeen = now
    device.save(update_fields=['LastSeen'])

    log.info(
        '[%s] %s | sensor="%s" | detalle="%s" | cat=%s | estado=%s | canal=%s',
        device.Name, origin, sensor_name, detalle, categoria, estado, canal,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Callbacks MQTT
# ─────────────────────────────────────────────────────────────────────────────

def _on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        log.info('Conectado al broker MQTT.')
        # Suscribir a todos los topics configurados
        for topic in userdata.get('topics', []):
            client.subscribe(topic)
            log.info('Suscrito a: %s', topic)
    else:
        log.error('Error de conexión MQTT, código: %s', rc)


def _on_disconnect(client, userdata, rc, properties=None, reason_code=None):
    log.warning('Desconectado del broker (rc=%s). Reconectando...', rc)


def _on_message(client, userdata, msg):
    topic   = msg.topic
    payload = msg.payload.decode('utf-8', errors='replace')
    log.debug('MQTT topic=%s payload=%s', topic, payload)
    try:
        _process_message(topic, payload)
    except Exception as exc:
        log.exception('Error procesando mensaje: %s', exc)


# ─────────────────────────────────────────────────────────────────────────────
# Construcción del cliente y bucle principal
# ─────────────────────────────────────────────────────────────────────────────

def _build_subscriptions(cli_broker: str | None, cli_port: int, cli_topic: str | None):
    """
    Carga dispositivos activos de la BD y agrupa sus topics por broker.
    Retorna: list of dict { broker, port, topics }
    """
    from Apps.SEGURIDAD.models import SecurityDevice

    # Agrupar por (broker, port)
    groups: dict[tuple, dict] = {}

    devices = SecurityDevice.objects.filter(Status='Active')
    for dev in devices:
        broker = (dev.MqttBroker or cli_broker or '').strip()
        port   = dev.MqttPort or cli_port
        topic  = (dev.MqttTopic or cli_topic or '').strip()

        if not broker or not topic:
            log.warning(
                'Dispositivo "%s" sin broker o topic configurado — omitido.',
                dev.Name,
            )
            continue

        key = (broker, port)
        if key not in groups:
            groups[key] = {'broker': broker, 'port': port, 'topics': []}
        groups[key]['topics'].append(topic)

    # Fallback: si hay broker/topic global pero ningún dispositivo lo usa
    if cli_broker and cli_topic and not groups:
        key = (cli_broker, cli_port)
        groups[key] = {'broker': cli_broker, 'port': cli_port, 'topics': [cli_topic]}

    return list(groups.values())


def _run_client(group: dict):
    """Inicia un cliente MQTT para un broker/grupo de topics."""
    broker = group['broker']
    port   = group['port']
    topics = group['topics']

    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id=f'seguridad-{broker}-{port}',
        userdata={'topics': topics},
    )
    client.on_connect    = _on_connect
    client.on_disconnect = _on_disconnect
    client.on_message    = _on_message

    log.info('Conectando a %s:%d — topics: %s', broker, port, topics)
    client.connect(broker, port, keepalive=60)
    client.loop_forever()


# ─────────────────────────────────────────────────────────────────────────────
# Punto de entrada
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='SEGURIDAD MQTT Client')
    parser.add_argument('--settings', help='Django settings module',
                        default=os.environ.get('DJANGO_SETTINGS_MODULE',
                                               'RopPumpWeb.settings.local'))
    parser.add_argument('--broker',  help='Broker MQTT global (override)', default=None)
    parser.add_argument('--port',    help='Puerto MQTT global', type=int, default=1883)
    parser.add_argument('--topic',   help='Topic MQTT global (override)', default=None)
    args = parser.parse_args()

    _setup_django(args.settings)

    groups = _build_subscriptions(args.broker, args.port, args.topic)

    if not groups:
        log.error(
            'No hay dispositivos activos con broker+topic configurados. '
            'Usa --broker y --topic como alternativa global, o configura '
            'los dispositivos en /seguridad/dispositivos/.'
        )
        sys.exit(1)

    if len(groups) == 1:
        # Caso simple: un solo broker → corre en el hilo principal
        _run_client(groups[0])
    else:
        # Múltiples brokers → un hilo por broker
        import threading
        threads = []
        for g in groups:
            t = threading.Thread(target=_run_client, args=(g,), daemon=True)
            t.start()
            threads.append(t)
        log.info('Clientes MQTT activos: %d broker(s).', len(threads))
        try:
            while True:
                _time.sleep(10)
        except KeyboardInterrupt:
            log.info('Detenido por el usuario.')


if __name__ == '__main__':
    main()
