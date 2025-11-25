from typing import Any
from django.contrib import admin
from django.db import models
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.utils.safestring import mark_safe
from tinymce.widgets import AdminTinyMCE

from cate.templatetags.format_day import format_day_html
from common.admin import CommonImagesInline

from .models import Day, DayImage


class DayImagesInline(CommonImagesInline):
    """
    Inline for images in days.
    """

    model = DayImage


@admin.register(Day)
class DayAdmin(admin.ModelAdmin):
    list_display = ("formatted_day", "child", "saint_name", "feast")
    formfield_overrides = {
        models.TextField: {"widget": AdminTinyMCE},
    }
    inlines = [DayImagesInline]

    @admin.display(description="Jour")
    def formatted_day(self, day: Day):
        return mark_safe(format_day_html(day.day) + " décembre")

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).select_related("child")
