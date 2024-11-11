from typing import Any
from django.contrib import admin
from django.db import models
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from tinymce.widgets import AdminTinyMCE

from common.admin import CommonImagesInline

from .models import Day, DayImage


class DayImagesInline(CommonImagesInline):
    """
    Inline for images in days.
    """

    model = DayImage


@admin.register(Day)
class DayAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {"widget": AdminTinyMCE},
    }
    inlines = [DayImagesInline]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).select_related("child")
