# Generated by Django 4.2.4 on 2023-08-14 11:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("aumonerie", "0017_alter_child_ecole"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="date",
            options={"ordering": ["start_date", "start_time"], "verbose_name": "date"},
        ),
        migrations.AlterField(
            model_name="child",
            name="signe",
            field=models.BooleanField(default=False, verbose_name="Signé"),
        ),
    ]