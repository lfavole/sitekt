from django.contrib import admin
from django.db import models
from tinymce.widgets import AdminTinyMCE

from .models import Day


@admin.register(Day)
class DayAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {"widget": AdminTinyMCE},
    }
