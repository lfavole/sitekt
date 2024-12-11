from django.apps import AppConfig
from django.db import DEFAULT_DB_ALIAS


def create_pages(
    app_config: AppConfig,
    verbosity=2,
    using=DEFAULT_DB_ALIAS,
    **_kwargs,
):
    """
    Automatically creates the default pages for the `common` app.
    """
    if app_config.name != "common":
        return

    Page = app_config.get_model("Page")  # type: ignore

    pages_in_db = list(Page.objects.all())

    if pages_in_db:
        if verbosity >= 2:
            print("Some pages are already in the database, skipping")
        return

    pages = [
        Page(
            title="Accueil",
            content="<h1>Bienvenue sur le site du caté !</h1>",
        ),
        Page(title="Inscription", content="inscription"),
    ]

    for view, title in {
        "dates": "Dates importantes",
        "documents": "Documents téléchargeables",
        "articles": "Articles / Photos",
    }.items():
        base_page = Page(title=title)
        pages.extend([
            base_page,
            Page(title="Caté", slug=f"{view}_cate", content=f"espacecate_{view}", parent_page=base_page),
            Page(title="Aumônerie", slug=f"{view}_aumonerie", content=f"aumonerie_{view}", parent_page=base_page),
        ])

    for i, page in enumerate(pages):
        if not page.slug:
            page.slug = page._generate_slug(False)
        page.order = i

    while pages:
        pages_to_save = []
        other_pages = []

        for page in pages:
            if not page.parent_page or page.parent_page.pk:
                pages_to_save.append(page)
            else:
                other_pages.append(page)

        pages = other_pages

        for page in pages_to_save:
            if any(page_in_db.slug == page.slug for page_in_db in pages_in_db):
                if verbosity >= 2:
                    print(f"Page '{page}' already exists")
                continue
            if verbosity >= 2:
                print(f"Adding page '{page}'")
            page.save()
