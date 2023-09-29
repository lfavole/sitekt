from datetime import date

from django import template
from django.utils import dateformat
from django.utils.dates import MONTHS

register = template.Library()

from django.utils.translation import get_language

from .format_day import format_day


def _format_date(value: date):
    parts: list[str] = []
    if get_language().lower().split("-")[0] == "fr":
        parts.append(format_day(value.day))
        parts.append(str(MONTHS[value.month]))  # evaluate lazy string
    else:
        parts.append(str(MONTHS[value.month]))  # same thing
        parts.append(dateformat.format(value, "jS"))
    parts.append(f"{value.year}")
    return parts


@register.filter
def format_date(value1: date, value2: date | None = None):
    """
    Returns the formatted dates with common elements removed.
    """
    if not value1:
        value1 = date.today()

    value1_f = _format_date(value1)
    if not value2:
        return " ".join(value1_f)

    value2_f = _format_date(value2)

    for el1, el2 in list(zip(value1_f, value2_f))[::-1]:
        if el1 != el2:
            break
        value1_f = value1_f[:-1]

    return " ".join(value1_f) + " – " + " ".join(value2_f)
