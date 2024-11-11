from django.apps import AppConfig
from django.db import DEFAULT_DB_ALIAS


def create_groups(
    app_config: AppConfig,
    verbosity=2,
    using=DEFAULT_DB_ALIAS,
    **_kwargs,
):
    """
    Automatically creates the two default groups for the `aumonerie` app.
    """
    if app_config.name != "aumonerie":
        return

    from .models import Group

    groups = [
        Group(name="Collège"),
        Group(name="Lycée"),
    ]
    Group.objects.using(using).bulk_create(groups, ignore_conflicts=True)

    if verbosity >= 2:
        for group in groups:
            print(f"Adding group '{group}'")
