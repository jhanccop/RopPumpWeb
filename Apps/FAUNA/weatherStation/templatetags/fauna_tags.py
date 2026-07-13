from datetime import timezone as dt_utc
from zoneinfo import ZoneInfo
from django import template

register = template.Library()

_LIMA_TZ = ZoneInfo('America/Lima')


@register.filter
def lima_date(dt, fmt='d/m/Y H:i'):
    """Convierte datetime naive (UTC) o aware a hora Lima y lo formatea.
    Usa solo stdlib Python — no llama localtime() ni date_format() de Django."""
    if dt is None:
        return ''
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=dt_utc.utc)
    local_dt = dt.astimezone(_LIMA_TZ)
    fmt_map = {
        'd': f'{local_dt.day:02d}',
        'm': f'{local_dt.month:02d}',
        'Y': f'{local_dt.year:04d}',
        'H': f'{local_dt.hour:02d}',
        'i': f'{local_dt.minute:02d}',
        's': f'{local_dt.second:02d}',
    }
    result = ''
    i = 0
    while i < len(fmt):
        c = fmt[i]
        if c == '\\' and i + 1 < len(fmt):
            result += fmt[i + 1]
            i += 2
        elif c in fmt_map:
            result += fmt_map[c]
            i += 1
        else:
            result += c
            i += 1
    return result
