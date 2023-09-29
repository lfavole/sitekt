from common.pdfs.authorization import Authorization
from common.pdfs.calendar import Calendar
from common.pdfs.list import List
from common.pdfs.meetings import Meetings
from common.pdfs.quick_list import QuickList
from common.views import (
    CommonArticleListView,
    CommonArticleView,
    CommonDateListView,
    CommonDocumentListView,
    CommonPageView,
    serve,
)
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


authorization = Authorization.as_view()
calendar = Calendar.as_view()
list = List.as_view()
quick_list = QuickList.as_view()
meetings = Meetings.as_view()


class ArticleListView(CommonArticleListView):
    model = Article


class ArticleView(CommonArticleView):
    model = Article


class DateListView(CommonDateListView):
    model = Date


class DocumentListView(CommonDocumentListView):
    model = Document


def serve_document(request, pk):
    return serve(request, get_object_or_404(Document, pk=pk))
