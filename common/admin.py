import datetime
import sys
from functools import partial
from typing import Type

from adminsortable2.admin import SortableAdminMixin
from django import forms
from django.contrib import admin
from django.contrib.admin.helpers import Fieldset
from django.contrib.admin.utils import model_ngettext
from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy
from django_dynamic_admin_forms.admin import DynamicModelAdminMixin

from tinymce.widgets import AdminTinyMCE
from common.models import (
    Article,
    ArticleImage,
    Date,
    DateCategory,
    Document,
    DocumentCategory,
    Group,
    ImageBase,
    Page,
    PageImage,
)

from .forms import DateForm
from .models import Attendance, Child, Year
from .models import SiteMessage
from .utils import detect_date_modified, generate_default_site_message

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


class PageImagesInline(CommonImagesInline):
    """
    Inline for page images.
    """

    model = PageImage
    extra = 0


class PageAdminForm(forms.ModelForm):
    """
    Form in the admin interface for pages.
    """

    model = Page

    class Meta:
        widgets = {
            "content": AdminTinyMCE(),
        }


@admin.register(Page)
class PageAdmin(SortableAdminMixin, admin.ModelAdmin):
    """
    Admin interface for pages.
    """

    form = PageAdminForm
    inlines = [PageImagesInline]


class ArticleImagesInline(CommonImagesInline):
    """
    Inline for article images.
    """

    model = ArticleImage
    extra = 0


class ArticleAdminForm(PageAdminForm):
    """
    Form in the admin interface for articles.
    """

    model = Article
    inlines = [ArticleImagesInline]


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """
    Admin interface for articles.
    """

    form = ArticleAdminForm
    list_display = ("title", "date")


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """
    Admin interface for groups.
    """

    list_display = ("name",)


class CommonChildAdmin(admin.ModelAdmin):
    """
    Admin interface for childs.
    """

    model: Type[Child]
    other_model: Type[Child]
    change_list_template = "admin/change_list_child.html"

    list_display = ("nom", "prenom", "classe", "paye", "signe", "photos_admin", "infos_admin", "groupe")
    list_display_links = ("nom", "prenom")
    readonly_fields = ("date_inscription",)
    search_fields = ("nom", "prenom")
    list_filter = (
        "groupe",
        "communion_cette_annee",
        "paye",
        "signe",
        "classe",
        "bapteme",
        "premiere_communion",
        "photos",
    )

    @property
    def fieldsets(self):
        return self.model.fieldsets

    @admin.display(description="Photos", boolean=True)
    def photos_admin(self, obj: Child):
        return obj.photos

    @admin.display(description="Infos", boolean=True)
    def infos_admin(self, obj: Child):
        return bool(obj.autres_infos)

    readonly_fields = ("date_inscription",)
    actions = ["mark_paid", "mark_signed", "change_group"]

    @admin.action(permissions=["change"], description=_("Mark as paid"))
    @message_user(pgettext_lazy("admin action message", "marked as paid"))
    def mark_paid(self, request, queryset):
        queryset.update(paye=True)

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

    def redirect_to(self, obj):
        # Get the name of the previously called function in the stack
        # (the one that called get_obj_does_not_exist_redirect)
        caller = sys._getframe(2).f_code.co_name
        view_name = f"admin:{obj._meta.app_label}_{obj._meta.model_name}_"
        if "delete" in caller:
            return redirect(view_name + "delete", obj.id)
        if "history" in caller:
            return redirect(view_name + "history", obj.id)
        return redirect(view_name + "change", obj.id)

    def _get_obj_does_not_exist_redirect(self, request, opts, object_id):
        try:
            return self.redirect_to(self.other_model.objects.get(pk=object_id))
        except self.other_model.DoesNotExist:
            return super()._get_obj_does_not_exist_redirect(request, opts, object_id)


class OldChildMixin:
    """
    Mixin for children from previous years.
    """


@admin.register(Date)
class DateAdmin(DynamicModelAdminMixin, admin.ModelAdmin):
    """
    Admin interface for dates.
    """

    list_display = ("name", "place", "start_date", "end_date", "start_time", "end_time", "time_text", "cancelled")
    form = DateForm
    dynamic_fields = ("alert_users", "alert_message")

    def get_dynamic_alert_users_field(self, data):
        """Show the checkbox only when another field is modified/present.

        We'll show it when at least one of the main fields has a value (name, start_date, start_time,
        end_time, place, cancelled) — this makes it appear when the user modifies something.
        """
        # If editing an existing Date, compare with stored values to detect modifications
        id_val = data.get("id") or data.get("pk")
        modified = False
        if id_val:
            try:
                orig = Date.objects.get(pk=id_val)
            except Date.DoesNotExist:
                pass
            else:
                modified = detect_date_modified(orig, data)

        hidden = not modified
        # default unchecked
        return None, False, hidden

    def get_dynamic_alert_message_field(self, data):
        """Return (queryset_or_None, value, hidden) for `alert_message`.

        `data` is a dict-like with other field values from the form.
        """
        # Centralized default message generation
        default = generate_default_site_message(
            data.get("name"),
            data.get("start_date"),
            data.get("start_time"),
            data.get("end_time"),
        )
        alert_val = data.get("alert_users")
        hidden = not alert_val
        return None, default, hidden

    def save_model(self, request, obj, form, change):
        """If the admin asked to alert users, create a SiteMessage.

        Uses a French-formatted date and attempts to choose correct article/gender.
        Falls back to provided message when non-empty.
        """
        # Determine if this is a modification of an existing Date
        original = None
        modified = False
        if change and obj.pk:
            try:
                original = Date.objects.get(pk=obj.pk)
            except Exception:
                original = None

        def val_str(v):
            if v is None:
                return ""
            if isinstance(v, (datetime.date, datetime.datetime)):
                return v.isoformat()
            if isinstance(v, datetime.time):
                return v.strftime("%H:%M")
            return str(v)

        if original is not None:
            for k in ("name", "start_date", "start_time", "end_time", "place", "cancelled"):
                newv = form.cleaned_data.get(k)
                oldv = getattr(original, k, None)
                if val_str(newv) != val_str(oldv):
                    modified = True
                    break

        # Save the Date instance first
        super().save_model(request, obj, form, change)

        try:
            alert = form.cleaned_data.get("alert_users")
            text = form.cleaned_data.get("alert_message")
        except Exception:
            alert = False
            text = ""

        if alert:
            if not text:
                text = generate_default_site_message(
                    form.cleaned_data.get("name"),
                    form.cleaned_data.get("start_date"),
                    form.cleaned_data.get("start_time"),
                    form.cleaned_data.get("end_time"),
                )

            # determine level: if editing and modified, force WARNING
            if change and modified:
                level = "WARNING"
            else:
                level = form.cleaned_data.get("alert_level") if hasattr(form, "cleaned_data") else "INFO"

            SiteMessage.objects.create(message=text, is_active=True, level=level or "INFO")


@admin.register(DateCategory)
class DateCategoryAdmin(SortableAdminMixin, admin.ModelAdmin):
    """
    Admin interface for date categories.
    """


class CommonAttendancesInline(admin.TabularInline):
    """
    Inline for attendances.
    """

    model = Attendance
    fields = ("child", "is_present", "has_warned")
    readonly_fields = ("child",)
    extra = 0
    can_delete = False

    class Media:
        css = {
            "all": ("admin/hide_original.css", "admin/attendances.css"),
        }
        js = ("admin/attendances.js",)


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
        self.attendance_class: Type[Attendance] = self.inlines[0].model

    def get_inlines(self, request, obj=None):
        if obj is None:  # add form
            return []
        return super().get_inlines(request, obj)  # type: ignore


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """
    Admin interface for documents.
    """

    list_display = ("title", "file")


@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for document categories.
    """

    list_display = ("title",)


@admin.register(SiteMessage)
class SiteMessageAdmin(admin.ModelAdmin):
    list_display = ("__str__", "level", "is_active", "created_at")
    list_filter = ("is_active", "level")
    ordering = ("-created_at",)
