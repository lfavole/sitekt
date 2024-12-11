from dataclasses import dataclass, field

from django import template
from django.shortcuts import resolve_url
from django.urls import NoReverseMatch, Resolver404, resolve, reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext

from common.models import Page
from common.views import PageView

register = template.Library()


@dataclass
class NavItem:
    page: Page | None
    subitems: list["NavItem"] = field(default_factory=list)

    def render(self, req_match):
        page = self.page
        if page is None:
            ret = "<ul>\n"
            ret += '<label class="fermer" for="menu-checkbox"></label>\n'
            for subitem in self.subitems:
                ret += subitem.render(req_match)
            ret += "</ul>\n"
            return mark_safe(ret)

        ret = ""
        href = None
        if page.content == "":
            href = "#"
        elif len(page.content) < 100 and page.content[0] != "<":
            try:
                href = reverse(page.content)
            except Resolver404:
                href = None

        if not href:
            href = reverse("page", kwargs={"slug": page.slug})

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
        if not page.content and not self.subitems:
            message.append("vide")

        if message:
            ret += f"<i>(<small>Page {', '.join(message)} :</small> "
        ret += escape(page.title)
        if message:
            ret += ")</i>"
        ret += "</a>"

        if self.subitems:
            ret += "<ul>\n"
            for subitem in self.subitems:
                ret += subitem.render(req_match)
            ret += "</ul>\n"
        ret += "</li>\n"

        return ret


@register.simple_tag(takes_context=True)
def nav(context):
    pages_list = list(PageView(request=context.request).get_queryset())

    def get_page(current_page):
        pages_query = [page for page in pages_list if page.parent_page == current_page]
        ret = NavItem(current_page)
        for page in pages_query:
            ret.subitems.append(get_page(page))
        return ret

    return get_page(None).render(context.request.resolver_match)

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
