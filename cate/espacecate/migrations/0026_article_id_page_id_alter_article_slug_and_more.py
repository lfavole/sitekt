# Generated by Django 4.2.3 on 2023-09-24 14:27

from common.migration_helpers import export_data, get_primary_key, import_data
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("espacecate", "0025_alter_meeting_options"),
    ]

    operations = [
        migrations.RunPython(export_data("espacecate"), import_data("espacecate", True)),
        migrations.AddField(
            model_name="article",
            name="id",
            field=models.BigAutoField(
                auto_created=True,
                default=get_primary_key(),
                primary_key=True,
                serialize=False,
                verbose_name="ID",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="page",
            name="id",
            field=models.BigAutoField(
                auto_created=True,
                default=get_primary_key(),
                primary_key=True,
                serialize=False,
                verbose_name="ID",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="article",
            name="slug",
            field=models.SlugField(
                editable=False, max_length=100, unique=True, verbose_name="Slug"
            ),
        ),
        migrations.AlterField(
            model_name="page",
            name="slug",
            field=models.SlugField(
                editable=False, max_length=100, unique=True, verbose_name="Slug"
            ),
        ),
        migrations.RunPython(import_data("espacecate"), export_data("espacecate", True)),
    ]
