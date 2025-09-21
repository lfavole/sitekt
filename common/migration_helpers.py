from collections import defaultdict
from itertools import chain
from typing import Type

from django.apps.registry import Apps
from django.core.serializers import deserialize, serialize
from django.db import models

from .models import get_default_group


def get_primary_key(min=0):
    """
    Returns a function that returns 1, 2, 3, ...
    """
    i = min

    def function():
        nonlocal i
        i += 1
        return i

    return function


all_exported_data = {}
# must be lower case to compare with {"model": "..."}
# put them in order for the foreign keys!
models_classes = [
    "group",
    "child",
    "meeting",
    "attendance",
    "documentcategory",
    "document",
    "article",
    "articleimage",
]


def _get_model_class(model):
    if hasattr(model, "_meta"):
        model = model._meta
    return str(model).split(".", 1)[1]


def export_data(app_or_apps):
    if isinstance(app_or_apps, str):
        app_or_apps = [app_or_apps]

    def real_export(app, apps: Apps, schema_editor):
        models_list = [apps.get_model(app, m) for m in models_classes]

        # Export ALL the objects, not only e.g. the recent (!= old) children!
        all_exported_data[app] = serialize("python", chain(*(model._base_manager.all() for model in models_list)))
        for model in models_list:
            model.objects.using(schema_editor.connection.alias).delete()

    def function(apps: Apps, schema_editor):
        for app in app_or_apps:
            real_export(app, apps, schema_editor)

    return function


def import_data(new_app):
    def function(apps: Apps, schema_editor):
        exported_data = []
        models_list = []

        for app, export in all_exported_data.items():
            exported_data.extend(export)
            models_list.extend(apps.get_model(app, m) for m in models_classes)

        if not exported_data:
            return

        # Fields that have a foreign key
        fields_to_check: dict[str, list[tuple[str, str]]] = {}
        for model in models_list:
            for field in model._meta.fields:
                if isinstance(field, models.ForeignKey) and _get_model_class(field.related_model) in models_classes:
                    fields_to_check.setdefault(str(model._meta), []).append(
                        (str(field.related_model._meta), field.name)
                    )

        pk_generators = {}
        old_to_new_pks: defaultdict[str, dict[str, str | int]] = defaultdict(dict)

        get_default_group()  # Create the default group

        # Change the PKs on the items, save the correspondence in `old_to_new_pks`
        for element in exported_data:
            model_name = element["model"]
            if _get_model_class(model_name) not in models_classes:
                continue
            fields = element["fields"].copy()
            for _linked_model, field in fields_to_check.get(model_name, []):
                del fields[field]

            last_model_name = model_name.split(".", 1)[-1]
            if last_model_name not in pk_generators:
                model = apps.get_model("common", last_model_name)
                biggest_pk = model.objects.aggregate(models.Max("pk"))["pk__max"] or 0
                pk_generators[last_model_name] = get_primary_key(biggest_pk)

            new_pk = pk_generators[last_model_name]()
            old_to_new_pks[model_name][element["pk"]] = new_pk
            element["pk"] = new_pk

        # Change the PKs on the foreign keys
        for element in exported_data:
            model_name = element["model"]
            if model_name not in fields_to_check:
                continue  # this should never happen
            for linked_model, field in fields_to_check[model_name]:
                element["fields"][field] = old_to_new_pks[linked_model].get(element["fields"][field])

        # Change the app name
        for element in exported_data:
            for app in all_exported_data:
                new_model = element["model"].replace(app, new_app, 1)
                if element["model"] != new_model:
                    element["model"] = new_model
                    break

        new_objects = deserialize("python", exported_data)

        obj_for_models: defaultdict[Type[models.Model], list[models.Model]] = defaultdict(list)
        for obj in new_objects:
            obj_for_models[type(obj.object)].append(obj.object)

        for model, objs in obj_for_models.items():
            model.objects.using(schema_editor.connection.alias).bulk_create(objs)

        all_exported_data.clear()

    return function


def merge(export_apps, import_app):
    def function(apps: Apps, schema_editor):
        export_data(export_apps)(apps, schema_editor)
        import_data(import_app)(apps, schema_editor)

    return function


def migrate_paye_forwards(app):
    def migrate(apps, schema_editor):
        Child = apps.get_model(app, "Child")
        for child in Child.objects.all():
            child.paye_checkbox = child.paye == "oui"
            child.save()

    return migrate


def migrate_paye_backwards(app):
    def migrate(apps, schema_editor):
        Child = apps.get_model(app, "Child")
        for child in Child.objects.all():
            child.paye = "oui" if child.paye_checkbox else "non"
            child.save()

    return migrate


def migrate_pages_forwards(apps, schema_editor):
    Page = apps.get_model("common", "Page")
    Page.objects.exclude(content__startswith="<").update(url=models.F("content"), content="")


def migrate_pages_backwards(apps, schema_editor):
    Page = apps.get_model("common", "Page")
    Page.objects.exclude(url="").update(content=models.F("url"), url="")
