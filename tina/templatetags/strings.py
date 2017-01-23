from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def strings(name):
    """
    Adapted from http://stackoverflow.com/questions/433162
    """
    return getattr(settings, 'STRINGS', {}).get(name, '')
