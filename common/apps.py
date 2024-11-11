from django.apps import AppConfig
from django.db.models.signals import post_migrate

from .management import create_pages


class CommonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "common"
    verbose_name = "Configuration globale"

    def ready(self):
        post_migrate.connect(
            create_pages,
            dispatch_uid="common.management.create_pages",
        )
