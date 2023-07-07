# Generated by Django 4.2 on 2023-07-07 13:54

from django.db import migrations
import storage.fields


class Migration(migrations.Migration):
    dependencies = [
        ("aumonerie", "0012_alter_imagefields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="child",
            name="photo",
            field=storage.fields.ImageField(
                blank=True, null=True, upload_to="", verbose_name="Photo"
            ),
        ),
    ]
