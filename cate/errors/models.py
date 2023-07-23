from typing import Any

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Error(models.Model):
    """
    A logged server error.
    """

    time = models.DateTimeField(_("time"), auto_now_add=True)
    error_class = models.CharField(_("error class"), max_length=50)
    message = models.CharField(_("error message"), max_length=150)
    url = models.CharField(_("URL"), max_length=150)
    content = models.TextField(_("HTML content"), editable=False)

    class Meta:
        verbose_name = _("error")
        ordering = ("-time",)

    def get_absolute_url(self):
        return reverse("errors:error", args=[self.pk])

    def __str__(self):
        return f"{self.error_class}: {self.message} at {self.url}"

    @classmethod
    def create_from_traceback_data(cls, tb_data: dict[str, Any], content: str):
        """
        Return a new `Error` from a traceback data (`ExceptionReporter.create_from_traceback_data()`).
        """
        return cls.objects.create(
            error_class=tb_data["exception_type"][0:50],
            message=tb_data["exception_value"][0:150],
            url=tb_data["request"].path_info[0:150],
            content=content,
        )
