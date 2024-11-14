from django.contrib import admin
from django.db import models
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
