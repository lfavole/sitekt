# Generated by Django 4.2 on 2023-07-06 12:06

from django.db import migrations
import storage.fields


class Migration(migrations.Migration):
    dependencies = [
        ("aumonerie", "0011_alter_date_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="articleimage",
            name="image",
            field=storage.fields.ImageField(upload_to="", verbose_name="Image"),
        ),
        migrations.AlterField(
            model_name="child",
            name="photo",
            field=storage.fields.ImageField(
                null=True, upload_to="", verbose_name="Photo"
            ),
        ),
        migrations.AlterField(
            model_name="document",
            name="file",
            field=storage.fields.FileField(
                null=True, upload_to="", verbose_name="File"
            ),
        ),
        migrations.AlterField(
            model_name="pageimage",
            name="image",
            field=storage.fields.ImageField(upload_to="", verbose_name="Image"),
        ),
    ]
