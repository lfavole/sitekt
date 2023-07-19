from typing import Type

from adminsortable2.admin import SortableAdminMixin
from common.models import CommonArticle, CommonArticleImage, CommonPage, CommonPageImage, ImageBase
from django import forms
from django.contrib import admin
from django.shortcuts import redirect, resolve_url
from django.utils.translation import gettext_lazy as _
from easy_thumbnails.fields import ThumbnailerImageField
from tinymce.widgets import AdminTinyMCE

from .models import CommonChild, Year
from .widgets import CustomImageClearableFileInput


@admin.action(description=_("Export selected %(verbose_name_plural)s"))
def export_selected(modeladmin, request, queryset):
	meta = modeladmin.model._meta
	return redirect(
		"export",
		"json",
		meta.app_label,
		meta.model_name,
		",".join(str(element.pk) for element in queryset),
	)


admin.site.add_action(export_selected)


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
	model: Type[CommonChild]
	change_list_template = "admin/change_list_child.html"

	list_display = ("nom", "prenom")  # this is not useful !
	list_display_links = ("nom", "prenom")

	@property
	def fieldsets(self):
		return self.model.fieldsets

	readonly_fields = ("date_inscription",)
	actions = ["mark_paid", "mark_signed"]

	@admin.action(description=_("Mark as paid"))
	def mark_paid(self, request, queryset):
		queryset.update(paye=True)

	@admin.action(description=_("Mark as signed"))
	def mark_signed(self, request, queryset):
		queryset.update(signe=True)

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
