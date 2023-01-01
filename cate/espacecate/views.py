from django.shortcuts import render
from utils.views import CommonArticleListView, CommonArticleView, CommonDocumentListView, CommonPageView

from .forms import SubscriptionForm
from .models import Article, Document, Page


class PageView(CommonPageView):
    model = Page


def subscription(request):
    return render(request, "espacecate/subscription.html", {"form": SubscriptionForm()})


class ArticleListView(CommonArticleListView):
    model = Article

class ArticleView(CommonArticleView):
    model = Article


class DocumentListView(CommonDocumentListView):
    model = Document
