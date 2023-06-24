# Generated by Django 4.2 on 2023-06-24 15:47

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("espacecate", "0009_add_pricefield"),
    ]

    operations = [
        migrations.AddField(
            model_name="child",
            name="communion_cette_annee",
            field=models.BooleanField(
                default=False, verbose_name="Communion cette année"
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="child",
            name="date_inscription",
            field=models.DateTimeField(
                auto_now_add=True,
                default=datetime.datetime(
                    1970, 1, 1, 0, 0, tzinfo=datetime.timezone.utc
                ),
                verbose_name="Date et heure d'inscription",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="child",
            name="autres_infos",
            field=models.TextField(blank=True, verbose_name="Autres informations"),
        ),
        migrations.AlterField(
            model_name="child",
            name="groupe",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="espacecate.group",
                verbose_name="Groupe",
            ),
        ),
        migrations.AlterField(
            model_name="child",
            name="paye",
            field=models.CharField(
                choices=[("non", "Non"), ("attente", "En attente"), ("oui", "Oui")],
                default="non",
                max_length=10,
                verbose_name="Payé",
            ),
        ),
    ]
