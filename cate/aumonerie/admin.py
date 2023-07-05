from common.admin import CommonArticleAdmin, CommonArticleImagesInline, CommonChildAdmin, CommonDateAdmin, CommonDocumentAdmin, CommonDocumentCategoryAdmin, CommonPageAdmin, CommonPageImagesInline
from django.contrib import admin
from uservisit.admin import CommonUserVisitAdmin

from .models import Article, ArticleImage, Child, Date, Document, DocumentCategory, Page, PageImage, UserVisit


@admin.register(UserVisit)
class UserVisitAdmin(CommonUserVisitAdmin):
	"""
	Admin interface for user visits of the aumonerie app.
	"""

class PageImagesInline(CommonPageImagesInline):
	"""
	Inline for page images of the aumonerie app.
	"""
	model = PageImage

@admin.register(Page)
class PageAdmin(CommonPageAdmin):
	"""
	Admin interface for pages of the aumonerie app.
	"""
	inlines = [PageImagesInline]

class ArticleImagesInline(CommonArticleImagesInline):
	"""
	Inline for article images of the aumonerie app.
	"""
	model = ArticleImage

@admin.register(Article)
class ArticleAdmin(CommonArticleAdmin):
	"""
	Admin interface for articles of the aumonerie app.
	"""
	inlines = [ArticleImagesInline]

@admin.register(Child)
class ChildAdmin(CommonChildAdmin):
	"""
	Admin interface for childs of the aumonerie app.
	"""

@admin.register(Document)
class DocumentAdmin(CommonDocumentAdmin):
	"""
	Admin interface for documents of the aumonerie app.
	"""

@admin.register(DocumentCategory)
class DocumentCategoryAdmin(CommonDocumentCategoryAdmin):
	"""
	Admin interface for document categories of the aumonerie app.
	"""

@admin.register(Date)
class DateAdmin(CommonDateAdmin):
	"""
	Admin interface for dates of the aumonerie app.
	"""
