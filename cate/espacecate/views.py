from common.pdfs.calendar import calendar_pdf
from common.views import CommonArticleListView, CommonArticleView, CommonDateListView, CommonDocumentListView, CommonPageView, serve
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

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

def serve_document(request, pk):
    return serve(request, get_object_or_404(Document, pk = pk))

def calendar(request):
    return HttpResponse(calendar_pdf("espacecate"), "application/pdf")
