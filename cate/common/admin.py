from typing import Type

from adminsortable2.admin import SortableAdminMixin
from cate.widgets import MarkdownEditor
from common.models import CommonArticle, CommonPage
from django import forms
from django.contrib import admin

from .models import Year


@admin.register(Year)
class YearAdmin(admin.ModelAdmin):
	list_display = ("formatted_year", "is_active")

class CommonPageAdminForm(forms.ModelForm):
	"""
	Form in the admin interface for pages (with Markdown editor).
	"""
	model: Type[CommonPage]
	class Meta:
		widgets = {
			"content": MarkdownEditor(attrs = {"style": "width: 90%; height: 100%;"}),
		}

class CommonPageAdmin(SortableAdminMixin, admin.ModelAdmin):
	"""
	Admin interface for pages.
	"""
	form = CommonPageAdminForm


class CommonArticleAdminForm(CommonPageAdminForm):
	"""
	Form in the admin interface for articles (with Markdown editor).
	"""
	model: Type[CommonArticle]

class CommonArticleAdmin(admin.ModelAdmin):
	"""
	Admin interface for articles.
	"""
	form = CommonArticleAdminForm
	list_display = ("title", "date")
	ordering = ("-date",)

class CommonDateAdmin(admin.ModelAdmin):
	"""
	Admin interface for dates.
	"""
	list_display = ("name", "place", "start_date", "end_date", "start_time", "end_time", "time_text", "cancelled")
	fields = ("name", "place", "start_date", "end_date", "start_time", "end_time", "time_text", "cancelled")
	ordering = ("-start_date",)

class CommonDocumentAdmin(admin.ModelAdmin):
	"""
	Admin interface for documents.
	"""
	list_display = ("title", "file")

class CommonDocumentCategoryAdmin(admin.ModelAdmin):
	"""
	Admin interface for document categories.
	"""
	list_display = ("title",)
