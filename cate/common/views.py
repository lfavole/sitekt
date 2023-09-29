import mimetypes
from pathlib import Path
from typing import Literal, Type
from urllib.parse import quote

from django.contrib.auth import get_permission_codename
from django.db.models import Model
from django.db.models.fields.files import FieldFile
from django.db.models.query_utils import Q
from django.http import FileResponse, HttpRequest, HttpResponseNotModified
from django.shortcuts import render
from django.utils.http import http_date
from django.utils.timezone import now
from django.views import generic
from django.views.static import was_modified_since

from .models import (
    CommonArticle,
    CommonDate,
    CommonDocument,
    CommonDocumentCategory,
    CommonPage,
)


def _encode_filename(filename: str):
    try:
        filename.encode("ascii")
        return 'filename="{}"'.format(filename.replace("\\", "\\\\").replace('"', r"\""))
    except UnicodeEncodeError:
        return "filename*=utf-8''{}".format(quote(filename))


def subscription_ok(request):
    return render(request, "common/subscription_ok.html")


def has_permission_for_view(view: generic.View, permission="view"):
    return has_permission(view.request, view.model, permission)  # type: ignore


def has_permission(request: HttpRequest, model: Type[Model], permission="view"):
    perm_name = model._meta.app_label + "." + get_permission_codename(permission, model._meta)
    return request.user.has_perm(perm_name)  # type: ignore


class BaseView(generic.View):
    """
    Base view with template and queryset selection.
    """

    context_object_name: str
    template_filename: str
    model: Type[Model]

    def get_queryset(self):  # pylint: disable=C0116
        admin = has_permission_for_view(self, "view")
        ret = self.model.objects.all()
        if not admin:
            if hasattr(self.model, "content"):
                ret = ret.filter(~Q(content__exact=""))
            if hasattr(self.model, "hidden"):
                ret = ret.filter(hidden=False)
            if hasattr(self.model, "date"):
                ret = ret.filter(date__lte=now())
        return ret

    @property
    def extra_context(self):  # pylint: disable=C0116
        return {"app": self.request.resolver_match.app_name}


class CommonPageView(BaseView, generic.DetailView):
    """
    View for a page.
    """

    model: Type[CommonPage]
    context_object_name = "page"
    template_name = "common/page.html"


class CommonArticleListView(BaseView, generic.ListView):
    """
    View for an article list.
    """

    model: Type[CommonArticle]
    context_object_name = "articles"
    template_name = "common/articles.html"


class CommonArticleView(BaseView, generic.DetailView):
    """
    View for an article.
    """

    model: Type[CommonArticle]
    context_object_name = "article"
    template_name = "common/article.html"


class CommonDateListView(BaseView, generic.ListView):
    """
    View for a date list.
    """

    model: Type[CommonDate]
    context_object_name = "dates"
    template_name = "common/dates.html"


class CommonDocumentListView(BaseView, generic.ListView):
    """
    View for an document list.
    """

    model: Type[CommonDocument]
    context_object_name = "docs"
    template_name = "common/docs.html"

    def get_queryset(self):
        return super().get_queryset().prefetch_related("categories")

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        ret: dict[Literal[""] | CommonDocumentCategory, list[CommonDocument]] = {"": []}

        obj: CommonDocument
        cat: CommonDocumentCategory
        for obj in self.object_list:  # type: ignore
            added = False
            for cat in obj.categories.all():
                if cat not in ret:
                    ret[cat] = []
                ret[cat].append(obj)
                added = True

            if not added:
                ret[""].append(obj)

        kwargs["docs_ordered"] = ret

        return kwargs


def serve(request, obj: CommonDocument | FieldFile | Path | str):
    """
    Return a response that serves a file.
    """
    if isinstance(obj, CommonDocument):
        obj = obj.file
    if isinstance(obj, FieldFile):
        obj = obj.path
    fullpath = Path(obj)

    # Respect the If-Modified-Since header.
    statobj = fullpath.stat()
    if not was_modified_since(request.META.get("HTTP_IF_MODIFIED_SINCE"), statobj.st_mtime):
        return HttpResponseNotModified()
    content_type, encoding = mimetypes.guess_type(str(fullpath))
    content_type = content_type or "application/octet-stream"
    response = FileResponse(fullpath.open("rb"), as_attachment=True, content_type=content_type)
    response.headers["Last-Modified"] = http_date(statobj.st_mtime)
    if encoding:
        response.headers["Content-Encoding"] = encoding
    return response
