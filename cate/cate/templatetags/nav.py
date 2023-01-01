from typing import Any

from django import template
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe
from espacecate.models import Page

register = template.Library()

@register.filter
def nav(value: list[tuple[Page, Any]]):
	def nav_list(liste: list[tuple[Page, Any]]):
		ret = "<ul>\n"
		for page, nested_pages in liste:
			if page.content == "":
				href = "#"
			elif page.content[0] != "#":
				href = reverse(page.content)
			else:
				href = reverse("espacecate:page", args = [page.slug])

			ret += "\t<li><a href=\"" + href + "\">"
			if page.hidden:
				ret += "<i>(<small>Page cachée :</small> "
			ret += escape(page.title)
			if page.hidden:
				ret += ")</i>"
			ret += "</a>"

			if nested_pages:
				ret += nav_list(nested_pages)
			ret += "</li>\n"
		ret += "</ul>\n"
		return ret

	return mark_safe(nav_list(value))
