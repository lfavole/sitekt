from argparse import Namespace
from django.contrib.sitemaps import Sitemap
from django.contrib.auth.models import AnonymousUser

from common.views import ArticleView, PageView


def get_queryset(view_class):
    return view_class(request=Namespace(method="GET", user=AnonymousUser())).get_queryset(nav=True)


class ArticlesSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        return [*get_queryset(ArticleView)]

    def lastmod(self, obj):
        return obj.date


class PagesSitemap(Sitemap):
    priority = 1

    def changefreq(self, obj):
        return "daily" if obj.content == "dates" else "weekly"

    def items(self):
        return [item for item in get_queryset(PageView) if item.get_absolute_url() != "#"]
