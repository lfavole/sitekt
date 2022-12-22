from django.db.models.query_utils import Q
from django.shortcuts import render
from django.views import generic

from .forms import SubscriptionForm
from .models import Article, Document, Page


class PageView(generic.DetailView):
    model = Page
    context_object_name = "page"
    template_name = "page.html"
    queryset = Page.objects.filter(~Q(content__exact = ""))

def subscription(request):
    return render(request, "subscription.html", {"form": SubscriptionForm()})

class ArticleListView(generic.ListView):
    model = Article
    context_object_name = "articles"
    template_name = "articles.html"

class ArticleView(generic.DetailView):
    model = Article
    context_object_name = "article"
    template_name = "article.html"
    queryset = Article.objects.filter(~Q(content__exact = ""))

class DocumentListView(generic.ListView):
    model = Document
    context_object_name = "docs"
    template_name = "docs.html"
