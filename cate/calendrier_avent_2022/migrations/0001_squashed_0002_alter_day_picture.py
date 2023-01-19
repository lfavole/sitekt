# Generated by Django 4.1.3 on 2023-01-19 18:05

from django.db import migrations, models
import storage.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("filer", "__first__"),
    ]

    operations = [
        migrations.CreateModel(
            name="Day",
            fields=[
                (
                    "day",
                    models.IntegerField(
                        primary_key=True, serialize=False, verbose_name="Jour"
                    ),
                ),
                ("child", models.CharField(max_length=100, verbose_name="Enfant")),
                (
                    "picture",
                    storage.fields.ImageField(
                        null=True, upload_to="", verbose_name="Photo"
                    ),
                ),
            ],
            options={
                "verbose_name": "Jour",
            },
        ),
    ]
