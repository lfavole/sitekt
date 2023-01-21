from common.views import CommonArticleListView, CommonArticleView, CommonDateListView, CommonDocumentListView, CommonPageView
from django.shortcuts import render

from .forms import SubscriptionForm
from .models import Article, Date, Document, Page


class PageView(CommonPageView):
    model = Page


def subscription(request):
    return render(request, "espacecate/subscription.html", {"form": SubscriptionForm()})


class ArticleListView(CommonArticleListView):
    model = Article

class ArticleView(CommonArticleView):
    model = Article


class DateListView(CommonDateListView):
    model = Date

class DocumentListView(CommonDocumentListView):
    model = Document
