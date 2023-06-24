from common.pdfs.authorization import authorization_pdf
from common.pdfs.calendar import calendar_pdf
from common.views import CommonArticleListView, CommonArticleView, CommonDateListView, CommonDocumentListView, CommonPageView, pdf_response, serve
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import SubscriptionForm
from .models import Article, Date, Document, Page


class PageView(CommonPageView):
    model = Page


def subscription(request):
    if request.method == "POST":
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("espacecate:inscription_ok")
    else:
        form = SubscriptionForm()
    return render(request, "common/subscription.html", {"title": "Inscription caté et éveil à la foi", "form": form})

def authorization(request):
    return pdf_response(request, authorization_pdf(request, "aumonerie"), "autorisation")


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
