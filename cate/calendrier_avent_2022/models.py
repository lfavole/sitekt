from django.db import models
from django.utils.safestring import mark_safe
from storage.fields import ImageField

from cate.templatetags.format_day import format_day, format_day_html


class Day(models.Model):
    day = models.fields.IntegerField("Jour", primary_key=True)
    child = models.fields.CharField("Enfant", max_length=100)
    picture = ImageField("Photo", null=True)

    class Meta:
        verbose_name = "Jour"

    def __str__(self):
        return mark_safe(format_day(self.day) + " décembre : " + self.child)

    def __html__(self):
        return mark_safe(format_day_html(self.day) + " décembre : " + self.child)
