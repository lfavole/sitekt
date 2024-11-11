from django.apps import AppConfig
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _


class TrackingConfig(AppConfig):
    name = "tracking"
    verbose_name = _("Visits")
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        from . import handlers
        from .models import Visit

        post_save.connect(handlers.post_save_cache, sender=Visit)
