# Generated by Django 4.2.3 on 2023-09-06 13:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("espacecate", "0021_remove_meeting_date_item"),
    ]

    operations = [
        migrations.AlterField(
            model_name="date",
            name="place",
            field=models.CharField(blank=True, max_length=100, verbose_name="Place"),
        ),
    ]