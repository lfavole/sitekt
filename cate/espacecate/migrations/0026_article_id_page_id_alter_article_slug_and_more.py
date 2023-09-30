# Generated by Django 4.2.3 on 2023-09-24 14:27

import django.db.models.deletion
import django.utils.timezone
from common.migration_helpers import export_data, import_data
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("espacecate", "0025_alter_meeting_options"),
    ]

    operations = [
        migrations.RunPython(export_data("espacecate"), export_data("espacecate", True)),
        migrations.DeleteModel("page"),
        migrations.DeleteModel("article"),
        migrations.CreateModel(
            name="Article",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("slug", models.SlugField(editable=False, max_length=100, unique=True, verbose_name="slug")),
                ("title", models.CharField(max_length=100, verbose_name="title")),
                ("content", models.TextField(blank=True, verbose_name="content")),
                ("date", models.DateField(default=django.utils.timezone.now, verbose_name="date")),
                ("hidden", models.BooleanField(default=False, verbose_name="hidden article")),
            ],
            options={
                "verbose_name": "article",
                "ordering": ["-date"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Page",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("slug", models.SlugField(editable=False, max_length=100, unique=True, verbose_name="slug")),
                ("title", models.CharField(max_length=100, verbose_name="title")),
                ("content", models.TextField(blank=True, verbose_name="content")),
                ("hidden", models.BooleanField(default=False, verbose_name="hidden page")),
                ("order", models.PositiveIntegerField(default=0, verbose_name="order")),
                (
                    "parent_page",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="espacecate.page",
                        verbose_name="Previous page",
                    ),
                ),
            ],
            options={
                "verbose_name": "page",
                "ordering": ["order"],
                "abstract": False,
            },
        ),
        migrations.RunPython(import_data("espacecate"), import_data("espacecate", True)),
    ]
