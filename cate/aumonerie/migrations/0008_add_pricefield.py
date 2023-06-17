# Generated by Django 4.2 on 2023-06-17 09:56

import common.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("aumonerie", "0007_fix_caps_on_field_names"),
    ]

    operations = [
        migrations.AlterField(
            model_name="child",
            name="frais",
            field=common.fields.PriceField(verbose_name="Participation aux frais"),
        ),
    ]
