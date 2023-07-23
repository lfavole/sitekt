from typing import Any

from django import template
from django.urls import NoReverseMatch, reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe
from espacecate.models import Page

register = template.Library()

@register.filter
def nav(value: list[tuple[Page, Any]]):
	def nav_list(liste: list[tuple[Page, Any]]):
		ret = "<ul>\n"
		for page, nested_pages in liste:
			href = None
			if page.content == "":
				href = "#"
			elif len(page.content) < 100 and page.content[0] != "<":
				try:
					href = reverse(page.content)
				except NoReverseMatch:
					href = None

			if not href:
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
