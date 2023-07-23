from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ErrorsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "errors"
    verbose_name = _("Errors")
