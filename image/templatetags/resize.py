from django import template
register = template.Library()

@register.filter
def resize(value, arg):
    arr = value.split('/')
    arr.insert(-1, str(arg))
    return '/'.join(arr)
