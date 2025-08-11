"""common URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', lambda _: HttpResponse("TODO"), name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', lambda _: HttpResponse("TODO"), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import importlib
from time import time
from django.conf import settings
from django.http import HttpResponse
from django.urls import path
from django.views.decorators.cache import cache_page
from django.views.i18n import JavaScriptCatalog

from . import views

common_patterns = [
    ("liste", "List", "list"),
    ("meetings", "Meetings", "meetings"),
]

urlpatterns = []
for app in ("espacecate", "aumonerie"):
    for route, view, name in common_patterns:
        route = route.replace("/", f"/{app}/", 1) if "/" in route else f"{route}/{app}"
        if not callable(view):
            view = getattr(importlib.import_module(f"{app}.views"), view)
            if hasattr(view, "as_view"):
                try:
                    view = view.as_view()
                except TypeError:
                    view = view.as_view(app)
        urlpatterns.append(path(route, view, name=f"{app}_{name}"))

urlpatterns += [
    path("articles/<slug:slug>", views.ArticleView.as_view(), name="article"),
    path("articles", views.ArticleListView.as_view(), name="articles"),
    path("autorisation", views.autorisation, name="autorisation"),
    path("calendrier", views.calendar, name="calendrier"),
    path("dates", views.DateListView.as_view(), name="dates"),
    path("dates-ics", views.dates_ics, name="dates_ics"),
    path("docs/<int:pk>", views.serve_document, name="document"),
    path("docs", views.DocumentListView.as_view(), name="documents"),
    path("inscription/ok/<int:pk>", views.subscription_ok, name="inscription_ok_pk"),
    path("inscription/ok", views.subscription_ok, name="inscription_ok"),
    path("inscription/new", views.subscription_new, name="inscription_nouveau"),
    path("inscription/<int:pk>", views.subscription_old, name="inscription_ancien"),
    path("inscription", views.subscription, name="inscription"),
    path("index", views.PageView.as_view(), kwargs={"slug": "accueil"}),
    path("jsi18n", cache_page(86400, key_prefix=time() if settings.DEBUG else 0)(JavaScriptCatalog.as_view(packages=["common"])), name="javascript-catalog"),
    path("liste-dates", views.dates_list, name="liste_dates"),
    path("", views.PageView.as_view(), name="accueil", kwargs={"slug": "accueil"}),
    path("<slug:slug>", views.PageView.as_view(), name="page"),
]

# Do not escape the dash in JavaScript, it causes issues with the minifier
from django.utils.html import _js_escapes
_js_escapes.pop(ord("-"))
