from calendrier_avent_2022.templatetags.format_day import format_day_html
from django.db import models
from django.utils.safestring import mark_safe
from filer.fields.image import FilerImageField


class Day(models.Model):
	day = models.fields.IntegerField("Jour", primary_key = True)
	child = models.fields.CharField("Enfant", max_length = 100)
	picture = FilerImageField(verbose_name = "Photo", null = True, on_delete = models.SET_NULL) # type: ignore

	class Meta:
		verbose_name = "Jour"

	def __str__(self):
		return mark_safe(format_day_html(self.day) + " décembre : " + self.child)
