# Generated by Django 4.2.7 on 2023-12-18 10:14

from django.db import migrations
import storage.fields


class Migration(migrations.Migration):
    dependencies = [
        ("calendrier_avent_2023", "0002_dayimage"),
    ]

    operations = [
        migrations.AlterField(
            model_name="day",
            name="picture",
            field=storage.fields.ImageField(blank=True, null=True, upload_to="", verbose_name="photo"),
        ),
    ]
