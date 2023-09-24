# Generated by Django 4.2.3 on 2023-09-24 08:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("aumonerie", "0022_alter_group_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="meeting",
            name="name",
            field=models.CharField(
                blank=True,
                help_text="Replaces the meeting kind",
                max_length=100,
                verbose_name="Name",
            ),
        ),
    ]
