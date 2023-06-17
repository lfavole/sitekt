# Generated by Django 4.2 on 2023-06-16 15:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("aumonerie", "0004_alter_documentcategory_title"),
    ]

    operations = [
        migrations.CreateModel(
            name="Group",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, verbose_name="Name")),
            ],
            options={
                "verbose_name": "group",
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="child",
            name="paye",
            field=models.BooleanField(default=False, verbose_name="Payé"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="child",
            name="signe",
            field=models.BooleanField(default=False, verbose_name="Signé"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="child",
            name="groupe",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="aumonerie.group",
                verbose_name="Groupe",
            ),
        ),
    ]
