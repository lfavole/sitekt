from typing import Type

from adminsortable2.admin import SortableAdminMixin
from django.http.request import HttpRequest
from common.models import CommonArticle, CommonArticleImage, CommonPage, CommonPageImage, ImageBase
from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from easy_thumbnails.fields import ThumbnailerImageField
from tinymce.widgets import AdminTinyMCE

from .models import Year
from .widgets import CustomImageClearableFileInput


@admin.register(Year)
class YearAdmin(admin.ModelAdmin):
	list_display = ("formatted_year", "is_active")

class CommonImagesInline(admin.TabularInline):
	"""
	Inline for images.
	"""
	model: Type[ImageBase]
	readonly_fields = ("image",)

	def has_add_permission(self, *args, **kwargs):
		return False

	def has_change_permission(self, *args, **kwargs):
		return False

class CommonPageImagesInline(CommonImagesInline):
	"""
	Inline for page images.
	"""
	model: Type[CommonPageImage]
	extra = 0

class CommonPageAdminForm(forms.ModelForm):
	"""
	Form in the admin interface for pages (with Markdown editor).
	"""
	model: Type[CommonPage]
	class Meta:
		widgets = {
			"content": AdminTinyMCE(),
		}

class CommonPageAdmin(SortableAdminMixin, admin.ModelAdmin):
	"""
	Admin interface for pages.
	"""
	form = CommonPageAdminForm


class CommonArticleImagesInline(CommonImagesInline):
	"""
	Inline for article images.
	"""
	model: Type[CommonArticleImage]
	extra = 0

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

class CommonGroupAdmin(admin.ModelAdmin):
	"""
	Admin interface for groups.
	"""
	list_display = ("name",)

class CommonChildAdmin(admin.ModelAdmin):
	"""
	Admin interface for childs.
	"""
	@property
	def fieldsets(self):
		return self.model.fieldsets

	readonly_fields = ("date_inscription",)
	formfield_overrides = {
		ThumbnailerImageField: {"widget": CustomImageClearableFileInput},
	}

class CommonDateAdmin(admin.ModelAdmin):
	"""
	Admin interface for dates.
	"""
	list_display = ("name", "place", "start_date", "end_date", "start_time", "end_time", "time_text", "cancelled")
	fields = ("name", "short_name", "place", "start_date", "end_date", "start_time", "end_time", "time_text", "cancelled")

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
