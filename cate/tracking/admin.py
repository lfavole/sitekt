from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import PageView, Visit
from .settings import TRACK_PAGEVIEWS


class PageviewInline(admin.TabularInline):
    model = PageView
    extra = 0
    can_delete = False
    fields = ["method", "url", "view_time"]

@admin.register(Visit)
class VisitorAdmin(admin.ModelAdmin):
    date_hierarchy = "start_time"

    list_display = ("session_key", "user", "start_time", "session_expired", "pretty_time_on_site", "ip_address")
    list_filter = ("user", "ip_address")

    readonly_fields = ("pretty_time_on_site",)
    exclude = ("time_on_site",)

    inlines = [PageviewInline]

    def has_add_permission(self, _request, _obj = None):
        return False
    def has_change_permission(self, _request, _obj = None):
        return False
    def has_delete_permission(self, _request, _obj = None):
        return False

class PageviewAdmin(admin.ModelAdmin):
    date_hierarchy = "view_time"

    list_display = ("url", "view_time")

    def has_add_permission(self, _request, _obj = None):
        return False
    def has_change_permission(self, _request, _obj = None):
        return False
    def has_delete_permission(self, _request, _obj = None):
        return False

if TRACK_PAGEVIEWS:
    admin.site.register(PageView, PageviewAdmin)
