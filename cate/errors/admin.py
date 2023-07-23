from django.contrib import admin

from .models import Error


@admin.register(Error)
class ErrorAdmin(admin.ModelAdmin):
    list_display = ("id", "time", "error_class", "message", "url")
    list_filter = ("time",)
    search_fields = ("id",)

    def has_add_permission(self, _request, _obj=None):
        return False

    def has_change_permission(self, _request, _obj=None):
        return False

    def has_delete_permission(self, _request, _obj=None):
        return False
