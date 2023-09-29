from django.contrib import admin
from django.contrib.staticfiles.storage import staticfiles_storage
from django.forms import Media
from django.utils.translation import gettext_lazy as _

from .models import PageView, Visit
from .settings import TRACK_PAGEVIEWS


class PageviewInline(admin.TabularInline):
    model = PageView
    extra = 0
    can_delete = False
    fields = ["method", "url", "view_time"]


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    date_hierarchy = "start_time"

    list_display = ("session_key", "user", "start_time", "session_expired", "pretty_time_on_site", "ip_address")
    list_filter = ("user", "ip_address")

    fields = [
        "session_key",
        "user",
        ("ip_address", "ip_address_location"),
        "user_agent",
        "pretty_user_agent",
        ("start_time", "expiry_time", "pretty_time_on_site"),
    ]

    @property
    def media(self):
        return super().media + Media(
            css={
                "all": [staticfiles_storage.url("admin/tracking.css")],
            }
        )

    inlines = [PageviewInline]

    def has_add_permission(self, _request, _obj=None):
        return False

    def has_change_permission(self, _request, _obj=None):
        return False

    def has_delete_permission(self, _request, _obj=None):
        return False


class PageviewAdmin(admin.ModelAdmin):
    date_hierarchy = "view_time"

    list_display = ("url", "view_time")

    def has_add_permission(self, _request, _obj=None):
        return False

    def has_change_permission(self, _request, _obj=None):
        return False

    def has_delete_permission(self, _request, _obj=None):
        return False


if TRACK_PAGEVIEWS:
    admin.site.register(PageView, PageviewAdmin)
