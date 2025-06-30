from common.pdfs.authorization import Authorization
from common.pdfs.calendar import Calendar
from common.pdfs.dates_list import DatesList
from common.pdfs.list import List
from common.pdfs.meetings import Meetings
from common.pdfs.quick_list import QuickList
from common.views import (
    CommonArticleListView,
    CommonArticleView,
    CommonDateListView,
    CommonDocumentListView,
    serve,
)
from django.shortcuts import get_object_or_404

from .models import Article, Date, Document


authorization = Authorization.as_view("aumonerie")
calendar = Calendar.as_view("aumoneire")
dates_list = DatesList.as_view("aumonerie")
list = List.as_view("aumonerie")
quick_list = QuickList.as_view("aumonerie")
meetings = Meetings.as_view("aumonerie")


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
