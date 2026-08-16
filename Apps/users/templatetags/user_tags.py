from django import template

register = template.Library()


@register.filter(name='has_app')
def has_app(user, app_code):
    """
    Uso en template:  {% if request.user|has_app:'seguridad' %}
    Devuelve True si el usuario tiene acceso a la app indicada.
    Superadmins siempre devuelven True.
    """
    if not user or not user.is_authenticated:
        return False
    return user.has_app_access(app_code)
