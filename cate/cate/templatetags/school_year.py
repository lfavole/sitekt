from datetime import date

from django import template

register = template.Library()

@register.filter
def school_year(value: date | None = None):
	"""
	Returns the school year for the given date or today.
	"""
	if not value:
		value = date.today()
	if value.month < 8:
		# month < August => first year is the previous year
		first_year = value.year - 1
	else:
		# month >= August => first year is this year
		first_year = value.year
	return str(first_year) + "-" + str(first_year + 1)
