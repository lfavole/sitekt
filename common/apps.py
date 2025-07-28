from django.apps import AppConfig
from django.db.models.signals import post_migrate

from .management import create_date_categories, create_pages, create_year


class CommonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "common"
    verbose_name = "Configuration globale"

    def ready(self):
        post_migrate.connect(
            create_date_categories,
            dispatch_uid="common.management.create_date_categories",
        )
        post_migrate.connect(
            create_pages,
            dispatch_uid="common.management.create_pages",
        )
        post_migrate.connect(
            create_year,
            dispatch_uid="common.management.create_year",
        )
