from functools import partial
from typing import Type

from adminsortable2.admin import SortableAdminMixin
from common.models import (
    CommonArticle,
    CommonArticleImage,
    CommonPage,
    CommonPageImage,
    ImageBase,
)
from django import forms
from django.contrib import admin
from django.contrib.admin.helpers import Fieldset
from django.contrib.admin.utils import model_ngettext
from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy
from tinymce.widgets import AdminTinyMCE

from .models import CommonAttendance, CommonChild, Year

admin.site.site_title = "Administration site du caté"
admin.site.site_header = "Administration du site du caté"
admin.site.index_title = _("Homepage")


def message_user(action=pgettext_lazy("admin action message", "changed")):
    def decorator(f):
        def wrapper(self: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
            ret = f(self, request, queryset)
            if ret is None:
                n = queryset.count()
                self.message_user(
                    request,
                    _("Successfully %(action)s %(count)d %(items)s.")
                    % {"action": action, "count": n, "items": model_ngettext(self.opts, n)},
                )
            return ret

        return wrapper

    return decorator


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
    Form in the admin interface for pages.
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
    Form in the admin interface for articles.
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
    actions = ["mark_paid", "mark_signed", "change_group"]

    @admin.action(permissions=["change"], description=_("Mark as paid"))
    @message_user(pgettext_lazy("admin action message", "marked as paid"))
    def mark_paid(self, request, queryset):
        queryset.update(paye="oui")

    @admin.action(permissions=["change"], description=_("Mark as signed"))
    @message_user(pgettext_lazy("admin action message", "marked as signed"))
    def mark_signed(self, request, queryset):
        queryset.update(signe=True)

    @admin.action(permissions=["change"], description=_("Change group"))
    @message_user(pgettext_lazy("admin action message", "changed group"))
    def change_group(self, request, queryset):
        ChangeGroupForm = forms.modelform_factory(
            self.model,
            fields=["groupe"],
            formfield_callback=partial(self.formfield_for_dbfield, request=request),
        )
        if request.POST.get("post"):
            form = ChangeGroupForm(request.POST)
            if form.is_valid():
                queryset.update(groupe=form.cleaned_data["groupe"])
                return
        else:
            form = ChangeGroupForm()

        context = {
            **self.admin_site.each_context(request),
            "media": self.media + form.media,
            "title": _("Change group"),
            "opts": self.model._meta,
            "form": form,
            "fieldset": Fieldset(form, fields=["groupe"]),
            "queryset": queryset,
            "action_checkbox_name": admin.helpers.ACTION_CHECKBOX_NAME,
        }
        return render(request, "admin/change_group.html", context)


class CommonDateAdmin(admin.ModelAdmin):
    """
    Admin interface for dates.
    """

    list_display = ("name", "place", "start_date", "end_date", "start_time", "end_time", "time_text", "cancelled")
    fields = (
        "name",
        "short_name",
        "place",
        "start_date",
        "end_date",
        "start_time",
        "end_time",
        "time_text",
        "cancelled",
    )


class CommonAttendancesInline(admin.TabularInline):
    """
    Inline for attendances.
    """

    model: Type[CommonAttendance]
    fields = ("child", "is_present", "has_warned")
    readonly_fields = ("child",)
    extra = 0
    can_delete = False

    class Media:
        css = {
            "all": ("admin/hide_original.css", "admin/attendances.css"),
        }


class CommonMeetingAdmin(admin.ModelAdmin):
    """
    Admin interface for meetings.
    """

    change_list_template = "admin/change_list_meeting.html"

    fields = ("date", "kind", "name")
    list_display = ("__str__", "date")
    # you must add `inlines = [CommonAttendancesInline]` to each subclass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attendance_class: Type[CommonAttendance] = self.inlines[0].model

    def get_inlines(self, request, obj=None):
        if obj is None:  # add form
            return []
        return super().get_inlines(request, obj)  # type: ignore


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
