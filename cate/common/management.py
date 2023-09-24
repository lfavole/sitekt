from typing import Type

from django.apps import AppConfig
from django.db import DEFAULT_DB_ALIAS


def create_pages(
    app_config: AppConfig,
    verbosity=2,
    using=DEFAULT_DB_ALIAS,
    **_kwargs,
):
    """
    Automatically creates the two default groups for the `aumonerie` app.
    """
    from common.models import CommonPage

    app = app_config.name
    if app not in ("espacecate", "aumonerie"):
        return

    Page: Type[CommonPage] = app_config.get_model("Page")  # type: ignore

    pages = [
        Page(
            title="Accueil",
            content="<h1>Bienvenue sur le site "
            + {"espacecate": "du caté", "aumonerie": "de l'aumônerie"}[app]
            + " !</h1>",
        ),
        Page(title="Inscription", content=f"{app}:inscription"),
        Page(title="Dates importantes", content=f"{app}:dates"),
        Page(title="Calendrier", content=f"{app}:calendrier"),
        Page(title="Documents téléchargeables", content=f"{app}:documents"),
        Page(title="Articles / Photos", content=f"{app}:articles"),
    ]
    for i, page in enumerate(pages):
        page.slug = page._generate_slug()
        page.order = i
    Page.objects.using(using).bulk_create(pages, ignore_conflicts=True)

    if verbosity >= 2:
        for page in pages:
            print(f"Adding page '{page}'")
