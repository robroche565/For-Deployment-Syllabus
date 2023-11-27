from django import template

register = template.Library()

@register.filter(name='alphabet')
def alphabet(value):
    return chr(ord('A') + value - 1)