from typing import Any

from django import template
from django.http import HttpRequest
from django.urls import Resolver404, resolve, reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe
from espacecate.models import Page

register = template.Library()

@register.filter
def nav(value: list[tuple[Page, Any]], request: HttpRequest):
	req_match = request.resolver_match

	def nav_list(liste: list[tuple[Page, Any]]):
		ret = "<ul>\n"
		for page, nested_pages in liste:
			href = None
			if page.content == "":
				href = "#"
			elif len(page.content) < 100 and page.content[0] != "<":
				try:
					href = reverse(page.content)
				except Resolver404:
					href = None

			if not href:
				href = reverse(request.resolver_match.app_name + ":page", kwargs = {"slug": page.slug})

			try:
				match = resolve(href) if href and href != "#" else None
			except Resolver404:
				match = None

			def is_active(match, req_match):
				if not match:
					return False

				# check for view_class if as_view() is used multiple times:
				# the returned function is not the same
				if (
					match.func != req_match.func
					and getattr(match.func, "view_class", 1) != getattr(req_match.func, "view_class", 2)
				):
					return False

				if match.args != req_match.args or match.kwargs != req_match.kwargs:
					return False

				return True

			ret += "\t<li><a" + (" class=\"act\"" if is_active(match, req_match) else "") + " href=\"" + href + "\">"
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
