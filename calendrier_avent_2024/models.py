from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from cate.templatetags.format_day import format_day, format_day_html
from common.models import ImageBase
from espacecate.models import Child


class Day(models.Model):
    day = models.fields.IntegerField("jour", unique=True)
    child = models.ForeignKey(Child, on_delete=models.CASCADE, verbose_name="enfant")
    holiday = models.fields.CharField("fête", max_length=100)
    content = models.fields.TextField("contenu", blank=True)

    class Meta:
        verbose_name = "Jour"

    def __str__(self):
        return mark_safe(format_day(self.day) + " décembre : " + str(self.child))

    def __html__(self):
        return mark_safe(format_day_html(self.day) + " décembre : " + str(self.child))

    def get_absolute_url(self):
        return reverse("calendrier_avent_2024:day", args=[self.day])


class DayImage(ImageBase):
    """
    An image in a day.
    """

    page = models.ForeignKey(Day, on_delete=models.CASCADE, verbose_name=_("Day"))  # type: ignore

    class Meta:
        verbose_name = _("day image")
        verbose_name_plural = _("day images")
