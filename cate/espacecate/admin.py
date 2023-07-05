from common.admin import CommonArticleImagesInline, CommonPageImagesInline
from common.admin import CommonArticleAdmin, CommonChildAdmin, CommonDateAdmin, CommonDocumentAdmin, CommonDocumentCategoryAdmin, CommonGroupAdmin, CommonPageAdmin
from django.contrib import admin
from uservisit.admin import CommonUserVisitAdmin

from .models import Article, ArticleImage, Child, Date, Document, DocumentCategory, Group, Page, PageImage, UserVisit


@admin.register(UserVisit)
class UserVisitAdmin(CommonUserVisitAdmin):
	"""
	Admin interface for user visits of the espacecate app.
	"""

class PageImagesInline(CommonPageImagesInline):
	"""
	Inline for page images of the espacecate app.
	"""
	model = PageImage

@admin.register(Page)
class PageAdmin(CommonPageAdmin):
	"""
	Admin interface for pages of the espacecate app.
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
	Admin interface for articles of the espacecate app.
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
	Admin interface for childs of the espacecate app.
	"""
	list_display = ("nom", "prenom", "paye", "signe", "groupe")
	readonly_fields = ("date_inscription",)
	search_fields = ("nom", "prenom")
	list_filter = ("groupe", "communion_cette_annee", "paye", "signe", "classe", "redoublement", "annees_kt", "annees_evf", "bapteme", "premiere_communion", "photos")

@admin.register(Document)
class DocumentAdmin(CommonDocumentAdmin):
	"""
	Admin interface for documents of the espacecate app.
	"""

@admin.register(DocumentCategory)
class DocumentCategoryAdmin(CommonDocumentCategoryAdmin):
	"""
	Admin interface for document categories of the espacecate app.
	"""

@admin.register(Date)
class DateAdmin(CommonDateAdmin):
	"""
	Admin interface for dates of the espacecate app.
	"""
