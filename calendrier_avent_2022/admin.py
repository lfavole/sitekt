from django.contrib import admin
from easy_thumbnails.fields import ThumbnailerField
from easy_thumbnails.widgets import ImageClearableFileInput

from .models import Day


@admin.register(Day)
class DayAdmin(admin.ModelAdmin):
    pass
