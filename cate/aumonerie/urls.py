"""aumonerie URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from . import views

app_name = "aumonerie"
urlpatterns = [
    path("articles/<slug:slug>", views.ArticleView.as_view(), name = "article"),
    path("articles/", views.ArticleListView.as_view(), name = "articles"),
    path("calendrier", views.calendar, name = "calendrier"),
    path("dates/", views.DateListView.as_view(), name = "dates"),
    path("docs/<int:pk>", views.serve_document, name = "document"),
    path("docs/", views.DocumentListView.as_view(), name = "documents"),
    path("inscription", views.subscription, name = "inscription"),
    path("index", views.PageView.as_view(), kwargs = {"slug": "accueil"}),
    path("", views.PageView.as_view(), name = "accueil", kwargs = {"slug": "accueil"}),
    path("<slug:slug>", views.PageView.as_view(), name = "page"),
]
