# Generated by Django 4.2.3 on 2023-09-24 08:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("espacecate", "0022_alter_date_place"),
    ]

    operations = [
        migrations.AlterField(
            model_name="group",
            name="name",
            field=models.CharField(max_length=100, unique=True, verbose_name="Name"),
        ),
    ]
