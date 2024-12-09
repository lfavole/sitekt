from typing import Any

from django import template
from django.http import HttpRequest
from django.shortcuts import resolve_url
from django.urls import NoReverseMatch, Resolver404, resolve, reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext
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
                href = reverse(request.resolver_match.app_name + ":page", kwargs={"slug": page.slug})

            try:
                match = resolve(href) if href and href != "#" else None
            except Resolver404:
                match = None

            def is_active(match, req_match):
                if not match:
                    return False

                # check for view_class if as_view() is used multiple times:
                # the returned function is not the same
                if match.func != req_match.func and getattr(match.func, "view_class", 1) != getattr(
                    req_match.func, "view_class", 2
                ):
                    return False

                if match.args != req_match.args or match.kwargs != req_match.kwargs:
                    return False

                return True

            ret += "\t<li><a" + (' class="act"' if is_active(match, req_match) else "") + ' href="' + href + '">'
            message = []
            if page.hidden:
                message.append("cachée")
            if not page.content and not nested_pages:
                message.append("vide")

            if message:
                ret += f"<i>(<small>Page {', '.join(message)} :</small> "
            ret += escape(page.title)
            if message:
                ret += ")</i>"
            ret += "</a>"

            if nested_pages:
                ret += nav_list(nested_pages)
            ret += "</li>\n"
        ret += "</ul>\n"
        return ret

    return mark_safe(nav_list(value))

@register.simple_tag(takes_context=True)
def nav_link(context, value, label, notrans=""):
    try:
        value = resolve_url(value)
    except NoReverseMatch:
        return ""
    if not value:
        return ""
    is_active = ' class="act"' if context.request.path == value else ""
    if notrans == "":
        label = mark_safe(gettext(label))
    elif notrans == "arrow":
        label = mark_safe('<span class="fleche fl-gauche"></span> ') + label
    elif notrans == "notrans":
        label = mark_safe(label)
    else:
        raise ValueError("Expected an empty string or notrans")
    return mark_safe(f'<li><a href="{escape(value)}"{is_active}>{label}</a></li>')
