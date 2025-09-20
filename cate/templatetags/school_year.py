from datetime import date

from django import template

from common.models import Year

register = template.Library()


@register.filter
def school_year(value: date | None = None):
    """
    Returns the school year for the given date or today.
    """
    return Year.get_for_date(date=value).formatted_year
