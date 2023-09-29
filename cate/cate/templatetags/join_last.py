from django import template
from django.template.defaultfilters import stringfilter
from django.utils.translation import gettext_lazy as _

register = template.Library()


@register.filter
def join_last(value: list, sep1=_(", "), sep2=_("and")):
    if len(value) < 2:
        return "".join(value)
    return sep1.join(value[:-1]) + " " + sep2 + " " + value[-1]
