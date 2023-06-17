from common.admin import CommonArticleAdmin, CommonDateAdmin, CommonDocumentAdmin, CommonDocumentCategoryAdmin, CommonGroupAdmin, CommonPageAdmin
from django.contrib import admin
from uservisit.admin import CommonUserVisitAdmin

from .models import Article, Child, Date, Document, DocumentCategory, Group, Page, UserVisit


@admin.register(UserVisit)
class UserVisitAdmin(CommonUserVisitAdmin):
	"""
	Admin interface for user visits of the espacecate app.
	"""

@admin.register(Page)
class PageAdmin(CommonPageAdmin):
	"""
	Admin interface for pages of the espacecate app.
	"""

@admin.register(Article)
class ArticleAdmin(CommonArticleAdmin):
	"""
	Admin interface for articles of the espacecate app.
	"""

@admin.register(Group)
class GroupAdmin(CommonGroupAdmin):
	"""
	Admin interface for groups of the espacecate app.
	"""

@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
	"""
	Admin interface for childs of the espacecate app.
	"""
	@property
	def fieldsets(self):
		return self.model.fieldsets

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
