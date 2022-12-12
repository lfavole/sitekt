from typing import Any

from django import template
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe
from espacecate.models import Page

register = template.Library()

@register.filter(name = "nav")
def nav(value: list[tuple[Page, Any]]):
	def nav_list(liste: list[tuple[Page, Any]]):
		ret = "<ul>\n"
		for link in liste:
			if link[0].content == "":
				href = "#"
			elif link[0].content[0] != "#":
				href = reverse(link[0].content)
			else:
				href = reverse("espacecate:page", args = [link[0].slug])
			ret += '\t<li><a href="' + href + '">' + escape(link[0].title) + "</a>"
			if link[1]:
				ret += nav_list(link[1])
			ret += "</li>\n"
		ret += "</ul>\n"
		return ret

	return mark_safe(nav_list(value))
