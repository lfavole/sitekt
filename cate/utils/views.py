from typing import Type

from django.contrib.auth import get_permission_codename
from django.db.models import Model
from django.db.models.query_utils import Q
from django.utils.timezone import now
from django.views import generic

from .models import CommonArticle, CommonDocument, CommonPage


def has_permission(view: generic.View, permission = "view"):
    model: Type[Model] = view.model # type: ignore
    perm_name = model._meta.app_label + "." + get_permission_codename(permission, model._meta)
    return view.request.user.has_perm(perm_name) # type: ignore

class BaseView(generic.View):
    """
    Base view with template and queryset selection.
    """
    context_object_name: str
    template_filename: str
    model: Type[Model]

    is_article = False

    def get_template_names(self): # pylint: disable=C0116
        app_name = self.request.resolver_match.app_name
        if not app_name:
            raise RuntimeError("No app name")
        return [app_name + "/" + self.template_filename]

    def get_queryset(self): # pylint: disable=C0116
        admin = has_permission(self, "view")
        ret = self.model.objects.all()
        if not admin:
            ret = ret.filter(~Q(content__exact = "")).filter(hidden = False)
            if self.is_article:
                ret = ret.filter(date__lte = now())
        return ret


class CommonPageView(BaseView, generic.DetailView):
    """
    View for a page.
    """
    model: Type[CommonPage]
    context_object_name = "page"
    template_filename = "page.html"


class CommonArticleListView(BaseView, generic.ListView):
    """
    View for an article list.
    """
    model: Type[CommonArticle]
    context_object_name = "articles"
    template_filename = "articles.html"
    is_article = True

class CommonArticleView(BaseView, generic.DetailView):
    """
    View for an article.
    """
    model: Type[CommonArticle]
    context_object_name = "article"
    template_filename = "article.html"
    is_article = True

class CommonDocumentListView(BaseView, generic.ListView):
    """
    View for an document list.
    """
    model: Type[CommonDocument]
    context_object_name = "docs"
    template_filename = "docs.html"
