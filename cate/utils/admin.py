from typing import Type

from adminsortable2.admin import SortableAdminMixin
from cate.widgets import MarkdownEditor
from django import forms
from django.contrib import admin
from utils.models import CommonArticle, CommonPage


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
