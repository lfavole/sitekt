from django.apps import AppConfig
from django.db.models.signals import post_migrate

from .management import create_groups


class AumonerieConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "aumonerie"
    verbose_name = "Aumônerie"

    def ready(self):
        post_migrate.connect(
            create_groups,
            dispatch_uid="aumonerie.management.create_groups",
        )
