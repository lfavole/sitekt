from common.pdfs.authorization import Authorization
from common.pdfs.list import List
from common.pdfs.meetings import Meetings
from common.pdfs.quick_list import QuickList
from common.views import (
    CommonArticleListView,
    CommonArticleView,
    CommonDocumentListView,
    serve,
)
from django.shortcuts import get_object_or_404

from .models import Article, Document


authorization = Authorization.as_view("espacecate")
list = List.as_view("espacecate")
quick_list = QuickList.as_view("espacecate")
meetings = Meetings.as_view("espacecate")


class ArticleListView(CommonArticleListView):
    model = Article


class ArticleView(CommonArticleView):
    model = Article


class DocumentListView(CommonDocumentListView):
    model = Document


def serve_document(request, pk):
    return serve(request, get_object_or_404(Document, pk=pk))
