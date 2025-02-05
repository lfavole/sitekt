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
from django.http import HttpResponse
from django.urls import path

from . import views

common_patterns = [
    ("articles/<slug:slug>", "ArticleView", "article"),
    ("articles/", "ArticleListView", "articles"),
    ("autorisation", "Authorization", "autorisation"),
    ("calendrier", "Calendar", "calendrier"),
    ("dates", "DateListView", "dates"),
    ("docs/<int:pk>", "serve_document", "document"),
    ("docs/", "DocumentListView", "documents"),
    ("liste", "List", "list"),
]

urlpatterns = []
for app in ("espacecate", "aumonerie"):
    for route, view, name in common_patterns:
        route = route.replace("/", f"/{app}/", 1) if "/" in route else f"{route}/{app}"
        if not callable(view):
            view = getattr(importlib.import_module(f"{app}.views"), view)
            if hasattr(view, "as_view"):
                view = view.as_view()
        urlpatterns.append(path(route, view, name=f"{app}_{name}"))

urlpatterns += [
    path("autorisation", lambda _: HttpResponse("TODO"), name="autorisation"),
    path("inscription/new", views.subscription_new, name="inscription_nouveau"),
    path("inscription/<str:site>/<int:pk>", views.subscription_old, name="inscription_ancien"),
    path("inscription", views.subscription, name="inscription"),
    path("index", views.PageView.as_view(), kwargs={"slug": "accueil"}),
    path("", views.PageView.as_view(), name="accueil", kwargs={"slug": "accueil"}),
    path("<slug:slug>", views.PageView.as_view(), name="page"),
]
