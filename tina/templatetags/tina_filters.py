from importlib import import_module

from django import template

register = template.Library()
_isinstance = isinstance


@register.filter
def isinstance(value, superclass):
    print('In filter|value: {}, superclass: {}'.format(value, superclass))
    root_module, terminal_class = superclass.rsplit('.', 1)
    return _isinstance(value, getattr(import_module(root_module), terminal_class))
