from common.admin import CommonArticleAdmin, CommonArticleImagesInline, CommonChildAdmin, CommonDateAdmin, CommonDocumentAdmin, CommonDocumentCategoryAdmin, CommonGroupAdmin, CommonPageAdmin, CommonPageImagesInline
from django.contrib import admin

from .models import Article, ArticleImage, Child, Date, Document, DocumentCategory, Group, Page, PageImage


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

@admin.register(Group)
class GroupAdmin(CommonGroupAdmin):
	"""
	Admin interface for groups of the espacecate app.
	"""

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
