# Generated by Django 4.1.3 on 2023-01-01 13:07

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("espacecate", "0020_rename_espacecateuservisit_uservisit_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="date",
            field=models.DateField(
                default=datetime.datetime(
                    2023, 1, 1, 13, 7, 26, 878131, tzinfo=datetime.timezone.utc
                ),
                verbose_name="Date",
            ),
        ),
    ]