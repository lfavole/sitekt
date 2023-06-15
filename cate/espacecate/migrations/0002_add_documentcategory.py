# Generated by Django 4.2 on 2023-06-15 11:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("espacecate", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="DocumentCategory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        blank=True, max_length=100, unique=True, verbose_name="Title"
                    ),
                ),
            ],
            options={
                "verbose_name": "document category",
                "verbose_name_plural": "document categories",
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="document",
            name="categories",
            field=models.ManyToManyField(
                blank=True, to="espacecate.documentcategory", verbose_name="Categories"
            ),
        ),
    ]
