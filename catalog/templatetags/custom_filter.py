from django import template

register = template.Library()


@register.filter
def excited(value):
    return f"{value}!!!"