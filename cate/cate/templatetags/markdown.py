# Source code for article:
# https://hakibenita.com/django-markdown

import re
from typing import Callable, Optional
from urllib.parse import parse_qs, urlparse

import markdown as md
from markdown.inlinepatterns import Pattern
from django import template
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.template.defaultfilters import stringfilter
from django.urls import NoReverseMatch, Resolver404, resolve, reverse
from django.utils.safestring import mark_safe
from markdown.inlinepatterns import LINK_RE, LinkInlineProcessor


class Error(Exception):
    pass

class InvalidMarkdown(Error):
    def __init__(self, error: str, value: Optional[str] = None) -> None:
        self.error = error
        self.value = value

    def __str__(self) -> str:
        if self.value is None:
            return self.error
        return f'{self.error} "{self.value}"';


def clean_link(href: str) -> str:
    if href.startswith("mailto:"):
        email_match = re.match("^(mailto:)?([^?]*)", href)
        if not email_match:
            raise InvalidMarkdown("Invalid mailto link", value = href)

        email = email_match.group(2)
        if email:
            try:
                EmailValidator()(email)
            except ValidationError:
                raise InvalidMarkdown("Invalid email address", value = email)

        return href

    # Remove fragments or query params before trying to match the url name
    href_parts = re.search(r"#|\?", href)
    if href_parts:
        start_ix = href_parts.start()
        url_name, url_extra = href[:start_ix], href[start_ix:]
    else:
        url_name, url_extra = href, ""

    try:
        url = reverse(url_name)
    except NoReverseMatch:
        pass
    else:
        return url + url_extra

    parsed_url = urlparse(href)

    if parsed_url.netloc == "":
        try:
            resolver_match = resolve(parsed_url.path)
        except Resolver404:
            raise InvalidMarkdown(
                "Should not use absolute links to the current site.\n"
                "We couldn't find a match to this URL. Are you sure it exists?",
                value = href,
            )
        else:
            raise InvalidMarkdown(
                f"Should not use absolute links to the current site.\n"
                f'Try using the url name "{resolver_match.url_name}".',
                value = href,
            )

    if parsed_url.scheme not in ("http", "https"):
        raise InvalidMarkdown("Must provide an absolute URL (be sure to include https:// or http://)", href)

    return href


class DjangoLinkInlineProcessor(LinkInlineProcessor):
    def getLink(self, data, index):
        href, title, index, handled = super().getLink(data, index)
        href = clean_link(href)
        return href, title, index, handled

class DjangoUrlExtension(md.Extension):
    def extendMarkdown(self, md, *args, **kwargs):
        md.inlinePatterns.register(DjangoLinkInlineProcessor(LINK_RE, md), "link", 160)


EMBED_PATTERN = r"\[!embed(\?(.*))?\]\((.*)\)"

class PyEmbedPattern(Pattern):
    def __init__(self, pyembed: "PyEmbed", md: md.Markdown):
        super().__init__(EMBED_PATTERN)
        self.pyembed = pyembed
        self.md = md

    def handleMatch(self, m):
        url = m.group(4)
        (max_width, max_height) = self._parse_params(m.group(3))
        for provider in self.pyembed.providers:
            for pattern in provider[0]:
                if re.search(pattern, url) is not None:
                    return self.md.htmlStash.store(provider[1](url, max_width, max_height))
        return f"""<iframe width="{max_width}" height="{max_height}" src="{url}" frameborder="0" allowfullscreen></iframe>"""

    def _parse_params(self, query_string):
        if not query_string:
            query_params = {}
        else:
            query_params = parse_qs(query_string)
        return (
            self._get_query_param(query_params, "max_width") or 400,
            self._get_query_param(query_params, "max_height") or 225,
        )

    @staticmethod
    def _get_query_param(query_params, name):
        if name in query_params:
            return int(query_params[name][0])
        return 0

class PyEmbed(md.Extension):
    def __init__(self):
        super().__init__()
        self.providers: list[tuple[list[str], Callable[[str, int, int], str]]] = []

    def add_provider(self, urls: list[str], callback: Callable[[str, int, int], str]):
        self.providers.append((urls, callback))

    def extendMarkdown(self, md: md.Markdown, _md_globals = None):
        md.inlinePatterns.register(PyEmbedPattern(self, md), "pyembed", 161)

pyembed = PyEmbed()


def video_id(value):
    """
    Get the video ID from an URL.
    """
    query = urlparse(value)
    if query.hostname == "youtu.be":
        return query.path[1:] # remove the slash
    if (query.hostname or "").removeprefix("www.") in ("youtube.com", "youtube-nocookie.com"):
        if query.path == "/watch":
            return parse_qs(query.query)["v"][0]
        if query.path.startswith("/embed/"):
            return query.path.split("/")[2]
        if query.path.startswith("/v/"):
            return query.path.split("/")[2]
    # fail?
    return None

def _youtube(url, width, height):
    id = video_id(url)
    return f"""<iframe width="{width}" height="{height}" src="https://www.youtube-nocookie.com/embed/{id}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen title="YouTube video player"></iframe>"""

pyembed.add_provider([r"^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(-nocookie)?\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"], _youtube)

md_instance = md.Markdown(extensions = ["nl2br", "extra", pyembed])

register = template.Library()

@register.filter(name = "markdown")
@stringfilter
def markdown(value):
    return mark_safe(md_instance.convert(value))
