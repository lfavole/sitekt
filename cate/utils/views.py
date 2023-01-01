from typing import Type

from django.db.models import Model
from django.db.models.query_utils import Q
from django.views import generic

from .models import CommonArticle, CommonDocument, CommonPage


class BaseView(generic.View):
    """
    Base view with template and queryset selection.
    """
    context_object_name: str
    template_filename: str
    model: Type[Model]

    def get_template_names(self):
        app_name = self.request.resolver_match.app_name
        if not app_name:
            raise RuntimeError("No app name")
        return [app_name + "/" + self.template_filename]

    def get_queryset(self):
        if self.request.user.is_staff: # type: ignore
            return self.model.objects.all()
        return self.model.objects.filter(~Q(content__exact = "")).filter(hidden = False)


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

class CommonArticleView(BaseView, generic.DetailView):
    """
    View for an article.
    """
    model: Type[CommonArticle]
    context_object_name = "article"
    template_filename = "article.html"

class CommonDocumentListView(BaseView, generic.ListView):
    """
    View for an document list.
    """
    model: Type[CommonDocument]
    context_object_name = "docs"
    template_filename = "docs.html"
