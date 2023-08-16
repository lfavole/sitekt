"""old_website URL Configuration

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
from django.urls import converters, path

from . import views


class OptionalPhpPathConverter:
    """
    Optional path that removes .php extension.
    """
    regex = r".*(\.php)?"

    def to_url(self, value: str):
        return value.removesuffix(".php")

    def to_python(self, value):
        return self.to_url(value)


converters.register_converter(OptionalPhpPathConverter, "optpath")


def all_apps(pattern, *args, with_app=False, kwargs=None, **real_kwargs):
    for app in ("espacecate", "aumonerie"):
        route_kwargs = kwargs.copy() if kwargs else {}
        if with_app:
            route_kwargs["app"] = app
        yield path(app + pattern, *args, kwargs=route_kwargs, **real_kwargs)


urlpatterns = [
    # Redirect app static files
    *all_apps("/includes/<optpath:path>", views.redirect_app_static),
    # Redirect kt-static to static
    path("kt-static/<optpath:path>", views.redirect_kt_static),

    # Redirect admin
    *all_apps("-admin/<optpath:path>", views.redirect_admin, with_app=True),

    # Redirect articles
    *all_apps("/articles.php", views.redirect_articles, with_app=True),

    # Show a message for the Advent calendar
    path("calendrier-avent/<optpath:path>", views.advent_calendar),

    # Redirect the other URLs normally (also removes .php extension)
    # path("<optpath:path>", views.simple_redirect),
]
