"""cate URL Configuration

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
import custom_settings
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.static import serve

from . import views

# from django.contrib.staticfiles.views import serve


handler404 = views.handler_404
handler500 = views.handler_500


def add_website(name: str):
    return path(name.replace("_", "-") + "/", include(name + ".urls", namespace=name))


urlpatterns = [
    path("admin/docs/", include("django.contrib.admindocs.urls")),
    path("admin/", admin.site.urls),
    add_website("aumonerie"),
    add_website("calendrier_avent_2022"),
    add_website("calendrier_avent_2023"),
    path("debug/", include("debug_toolbar.urls")),
    add_website("errors"),
    add_website("espacecate"),
    path("export/<format>/<app_label>/<model_name>/<elements_pk>", views.export, name="export"),
    path("google<str:id>.html", views.google),
    path("old/", include("old_website.urls")),
    path("robots.txt", views.robots),
    path("tinymce/upload-image", views.upload_image, name="tinymce-upload-image"),
    path("tinymce/", include("tinymce.urls")),
    path("tracking/", include("tracking.urls")),
    path("", views.home, name="home"),
    path("reload-website/", views.reload_website),
    # re_path(r'^', include('filer.server.urls')),
]

if not custom_settings.PYTHONANYWHERE:
    # urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT or "")
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT or "")
    urlpatterns += [
        path(settings.STATIC_URL.lstrip("/") + "<path:path>", serve, {"document_root": settings.STATIC_ROOT})
    ]
    urlpatterns += [path(settings.MEDIA_URL.lstrip("/") + "<path:path>", serve, {"document_root": settings.MEDIA_ROOT})]
