from datetime import timezone as dt_utc
from zoneinfo import ZoneInfo
from django import template

register = template.Library()

_LIMA_TZ = ZoneInfo('America/Lima')

_COMPASS_POINTS = (
    ('NNE', 11.25), ('NE', 33.75), ('ENE', 56.25), ('E', 78.75),
    ('ESE', 101.25), ('SE', 123.75), ('SSE', 146.25), ('S', 168.75),
    ('SSO', 191.25), ('SO', 213.75), ('OSO', 236.25), ('O', 258.75),
    ('ONO', 281.25), ('NO', 303.75), ('NNO', 326.25), ('N', 348.75),
    ('N', 360),
)


@register.filter
def wind_compass(deg):
    """Convierte grados (0-360) a punto cardinal (N, NNE, NE, ... NNO)."""
    if deg is None:
        return None
    try:
        d = float(deg) % 360
    except (TypeError, ValueError):
        return None
    for name, upper_bound in _COMPASS_POINTS:
        if d < upper_bound:
            return name
    return 'N'


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
