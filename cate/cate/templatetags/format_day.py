from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="format_day_html")
def format_day_html(value):
    value = int(value)
    return mark_safe(str(value) + ("<sup>er</sup>" if value == 1 else ""))


@register.filter(name="format_day")
def format_day(value):
    value = int(value)
    return mark_safe(str(value) + ("er" if value == 1 else ""))
