from common.pdfs.calendar import calendar_pdf
from common.views import CommonArticleListView, CommonArticleView, CommonDateListView, CommonDocumentListView, CommonPageView
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .forms import SubscriptionForm
from .models import Article, Date, Document, Page


class PageView(CommonPageView):
    model = Page


def subscription(request):
    form = SubscriptionForm()
    if request.method == "POST":
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("espacecate:inscription_ok")
    return render(request, "espacecate/subscription.html", {"form": form})


class ArticleListView(CommonArticleListView):
    model = Article

class ArticleView(CommonArticleView):
    model = Article


class DateListView(CommonDateListView):
    model = Date

class DocumentListView(CommonDocumentListView):
    model = Document

def calendar(request):
    return HttpResponse(calendar_pdf("espacecate"), "application/pdf")
