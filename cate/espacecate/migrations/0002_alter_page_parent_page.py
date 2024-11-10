# Generated by Django 5.1.2 on 2024-11-10 13:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("espacecate", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="page",
            name="parent_page",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="parent_pages",
                to="espacecate.page",
                verbose_name="Previous page",
            ),
        ),
    ]
