# Generated by Django 4.2.3 on 2023-09-21 17:24

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="user",
            options={
                "permissions": [("can_see_debug_toolbar", "Can see debug toolbar")],
                "verbose_name": "user",
            },
        ),
    ]