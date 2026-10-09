"""
Envío de notificaciones por Telegram para la app SEGURIDAD.
=============================================================
Módulo compartido entre:
  - scripts/SEGURIDAD/client.py  (cliente MQTT en background)
  - Apps/SEGURIDAD/views.py      (botón "Enviar prueba" del panel de configuración)

Usa la API HTTP de Telegram Bot (https://core.telegram.org/bots/api) vía `requests`,
sin dependencias adicionales.
"""

import logging
import time

import requests

log = logging.getLogger('seguridad.telegram')

TELEGRAM_API = 'https://api.telegram.org/bot{token}/sendMessage'
TIMEOUT = 8  # segundos

CATEGORY_LABEL = {'critico': 'CRÍTICO', 'alto': 'ALTO', 'informativo': 'INFORMATIVO'}
CATEGORY_EMOJI = {'critico': '🔴', 'alto': '🟠', 'informativo': 'ℹ️'}

# ── Anti-spam en memoria del proceso ────────────────────────────────────────
# key -> último timestamp (time.monotonic()) de envío
_last_sent: dict = {}


def _cooldown_ok(key, cooldown_seconds: int) -> bool:
    if cooldown_seconds <= 0:
        return True
    now  = time.monotonic()
    last = _last_sent.get(key)
    if last is not None and (now - last) < cooldown_seconds:
        return False
    _last_sent[key] = now
    return True


def send_message(bot_token: str, chat_id: str, text: str):
    """Envía un mensaje de texto a un chat_id. Retorna (ok: bool, error: str|None)."""
    if not bot_token:
        return False, 'Token del bot no configurado.'
    if not chat_id:
        return False, 'Chat ID vacío.'

    url = TELEGRAM_API.format(token=bot_token)
    try:
        resp = requests.post(
            url,
            json={'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'},
            timeout=TIMEOUT,
        )
        data = resp.json()
        if resp.status_code == 200 and data.get('ok'):
            return True, None
        return False, data.get('description', f'HTTP {resp.status_code}')
    except requests.RequestException as exc:
        return False, str(exc)


def _send_to_recipients(recipients, text, key_prefix, cooldown_seconds, bot_token):
    """Envía `text` a cada destinatario habilitado, respetando el cooldown."""
    sent = 0
    for recipient in recipients:
        key = (key_prefix, recipient.pk)
        if not _cooldown_ok(key, cooldown_seconds):
            log.debug('Cooldown activo para %s — omitido.', recipient)
            continue
        ok, err = send_message(bot_token, recipient.ChatID, text)
        if ok:
            sent += 1
            log.info('Telegram enviado a %s.', recipient)
        else:
            log.warning('Error enviando Telegram a %s: %s', recipient, err)
    return sent


def notify_event(device, sensor_name: str, categoria: str, estado: str, detalle: str):
    """
    Evalúa la configuración global (TelegramConfig) + destinatarios (TelegramRecipient)
    y envía la notificación de un evento de seguridad si corresponde.
    """
    from .models import TelegramConfig, TelegramRecipient

    cfg = TelegramConfig.get_solo()
    if not cfg.Enabled or not cfg.BotToken:
        return

    if cfg.OnlyActiveState and estado != 'activo':
        return

    recipients = TelegramRecipient.objects.filter(Enabled=True)
    recipients = [r for r in recipients if r.wants_category(categoria)]
    if not recipients:
        return

    emoji = CATEGORY_EMOJI.get(categoria, '🔔')
    label = CATEGORY_LABEL.get(categoria, categoria.upper())
    text = (
        f'{emoji} <b>[{label}]</b> {device.Name}\n'
        f'Sensor: {sensor_name or "—"}\n'
        f'Estado: {estado}\n'
        f'Detalle: {detalle or "—"}'
    )
    if device.Location:
        text += f'\nUbicación: {device.Location}'

    key_prefix = ('event', device.pk, sensor_name, categoria)
    _send_to_recipients(recipients, text, key_prefix, cfg.CooldownSeconds, cfg.BotToken)


def notify_offline(device):
    """Notifica que un dispositivo dejó de reportarse (escenario: desconexión)."""
    from .models import TelegramConfig, TelegramRecipient

    cfg = TelegramConfig.get_solo()
    if not cfg.Enabled or not cfg.BotToken or not cfg.NotifyDeviceOffline:
        return

    recipients = TelegramRecipient.objects.filter(Enabled=True, NotifyDeviceOffline=True)
    if not recipients:
        return

    text = (
        f'⚠️ <b>[DESCONEXIÓN]</b> {device.Name}\n'
        f'Sin reportarse hace más de {cfg.OfflineThresholdMinutes} min.'
    )
    if device.Location:
        text += f'\nUbicación: {device.Location}'

    key_prefix = ('offline', device.pk)
    _send_to_recipients(recipients, text, key_prefix, cfg.CooldownSeconds, cfg.BotToken)


def notify_reconnect(device):
    """Notifica que un dispositivo volvió a reportarse (escenario: reconexión)."""
    from .models import TelegramConfig, TelegramRecipient

    cfg = TelegramConfig.get_solo()
    if not cfg.Enabled or not cfg.BotToken or not cfg.NotifyDeviceReconnect:
        return

    recipients = TelegramRecipient.objects.filter(Enabled=True, NotifyDeviceReconnect=True)
    if not recipients:
        return

    text = f'✅ <b>[RECONECTADO]</b> {device.Name}\nVuelve a reportarse con normalidad.'
    if device.Location:
        text += f'\nUbicación: {device.Location}'

    key_prefix = ('reconnect', device.pk)
    _send_to_recipients(recipients, text, key_prefix, cfg.CooldownSeconds, cfg.BotToken)


def send_test(recipient) -> tuple:
    """Envía un mensaje de prueba a un TelegramRecipient puntual. Retorna (ok, error)."""
    from .models import TelegramConfig

    cfg = TelegramConfig.get_solo()
    if not cfg.BotToken:
        return False, 'Configura primero el Token del Bot.'

    text = (
        '🧪 <b>Mensaje de prueba</b>\n'
        'Las notificaciones de SEGURIDAD están configuradas correctamente para este destinatario.'
    )
    return send_message(cfg.BotToken, recipient.ChatID, text)
