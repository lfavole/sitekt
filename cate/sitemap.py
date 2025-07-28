from argparse import Namespace
from django.contrib.sitemaps import Sitemap
from django.contrib.auth.models import AnonymousUser

from aumonerie.views import ArticleView as AumonerieArticleView
from common.views import PageView
from espacecate.views import ArticleView as EspacecateArticleView


def get_queryset(view_class):
    return view_class(request=Namespace(method="GET", user=AnonymousUser())).get_queryset()


class ArticlesSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        return [
            *get_queryset(AumonerieArticleView),
            *get_queryset(EspacecateArticleView),
        ]

    def lastmod(self, obj):
        return obj.date


class PagesSitemap(Sitemap):
    priority = 1

    def changefreq(self, obj):
        return "daily" if obj.content == "dates" else "weekly"

    def items(self):
        return [item for item in get_queryset(PageView) if item.get_absolute_url() != "#"]
