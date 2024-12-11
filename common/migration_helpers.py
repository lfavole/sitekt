from collections import defaultdict
from itertools import chain
from typing import Type

from django.apps.registry import Apps
from django.core.serializers import deserialize, serialize
from django.db import models

from .models import Page


def get_primary_key():
    """
    Returns a function that returns 1, 2, 3, ...
    """
    i = 0

    def function():
        nonlocal i
        i += 1
        return i

    return function


all_exported_data = {}
# must be lower case to compare with {"model": "..."}
models_classes = ["page", "pageimage", "article", "articleimage"]


def _get_model_class(model):
    if hasattr(model, "_meta"):
        model = model._meta
    return str(model).split(".", 1)[1]


def export_data(app, reverse=False):
    def function(apps: Apps, schema_editor):
        models_list = [apps.get_model(app, m) for m in models_classes]

        all_exported_data[app] = serialize("python", chain(*(model.objects.all() for model in models_list)))
        for model in models_list:
            model.objects.using(schema_editor.connection.alias).delete()

    return function


def import_data(app, reverse=False):
    def function(apps: Apps, schema_editor):
        exported_data = all_exported_data.get(app)
        if not exported_data:
            return

        models_list = [apps.get_model(app, m) for m in models_classes]

        # Fields that have a foreign key to a page/article
        fields_to_check: dict[str, list[tuple[str, str]]] = {}
        for model in models_list:
            for field in model._meta.fields:
                if isinstance(field, models.ForeignKey) and _get_model_class(field.related_model) in models_classes:
                    fields_to_check.setdefault(str(model._meta), []).append(
                        (str(field.related_model._meta), field.name)
                    )

        pk_generators = defaultdict(get_primary_key)
        old_to_new_pks: dict[str, dict[str, str | int]] = {}

        # Change the PKs on the pages/articles, save the correspondence in `old_to_new_pks`
        for element in exported_data:
            model_name = element["model"]
            if _get_model_class(model_name) not in models_classes:
                continue
            fields = element["fields"].copy()
            for _linked_model, field in fields_to_check.get(model_name, []):
                del fields[field]
            new_pk = (
                # we must use the method from CommonPage because the models in migrations don't have methods
                Page._generate_slug(apps.get_model(model_name)(**fields))
                if reverse  # type: ignore
                else pk_generators[model_name]()
            )
            corr_for_model = old_to_new_pks.setdefault(model_name, {})
            corr_for_model[element["pk"]] = new_pk
            if not reverse:
                element["fields"]["slug"] = element["pk"]  # add the slug
            element["pk"] = new_pk

        # Change the PKs on the foreign keys
        for element in exported_data:
            model_name = element["model"]
            if model_name not in fields_to_check:
                continue  # this should never happen
            for linked_model, field in fields_to_check[model_name]:
                element["fields"][field] = old_to_new_pks[linked_model].get(element["fields"][field])

        new_objects = deserialize("python", exported_data)

        obj_for_models: dict[Type[models.Model], list[models.Model]] = {}
        for obj in new_objects:
            obj_for_models.setdefault(type(obj.object), []).append(obj.object)

        for model, objs in obj_for_models.items():
            model.objects.using(schema_editor.connection.alias).bulk_create(objs)

        del all_exported_data[app]

    return function
