import re
from datetime import date
from typing import Type

from cate.utils.text import slugify
from common.models import CommonArticle
from django.apps import apps
from django.contrib import messages
from django.contrib.staticfiles import finders
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, resolve_url
from django.urls import reverse
from django.contrib.staticfiles.storage import staticfiles_storage


def redirect_kt_static(request, path):
    if path == "style.css":
        path = "global.css"
    path = f"global/{path}"
    return redirect_static(request, path)


def redirect_app_static(request, path, app):
    return redirect_static(request, f"{app}/{path}")


def redirect_static(request, path):
    # target: str = finders.find(path)  # type: ignore
    target: str = staticfiles_storage.url(path)
    if not target:
        raise Http404
    return HttpResponseRedirect(target)


def redirect_admin(request, path):
    if not request.user:
        messages.add_message(
            request,
            messages.INFO,
            "Vous avez été redirigé vers le nouvel espace administrateur. "
            "Vos identifiants sont les mêmes que sur l'ancien site."
        )
    return HttpResponseRedirect(reverse("admin:index") + path)


def _old_slugify(text):
    if not text:
        return ""
    text = slugify(text)
    text = re.sub(r"\bnoel\b", "noe", text)  # it was a bug !!!
    text = re.sub(r"\b([dl](|a|es?)|[daq]u|aux|ou|e[tn]|il)\b", "", text)
    text = re.sub(r"--", "-", text).strip("-")
    text = text.replace("-", "_")
    return text


def redirect_articles(request, app):
    not_found = HttpResponseRedirect(resolve_url(app + ":articles"))

    id = _old_slugify(request.GET.get("id", ""))

    if not id or len(id) < 20:
        # avoid hitting the database for a short ID that doesn't exist
        return not_found

    Article: Type[CommonArticle] = apps.get_model(app, "Article")  # type: ignore
    # get only old articles
    articles = Article.objects.filter(date__lt=date(2023, 8, 1))

    for article in articles:
        print(_old_slugify(article.title))
        if _old_slugify(article.title) == id:
            return HttpResponseRedirect(resolve_url(app + ":article", slug=article.slug))

    return not_found


def advent_calendar(request, path):
    return render(request, "old_website/advent_calendar.html", status=404)


def simple_redirect(request, path, prefix=""):
    return HttpResponseRedirect(f"/{prefix}{path}")
