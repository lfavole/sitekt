# Generated by Django 5.1.4 on 2024-12-10 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("espacecate", "0003_remove_page_models"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="child",
            name="annee_pardon",
        ),
        migrations.RemoveField(
            model_name="child",
            name="annees_evf",
        ),
        migrations.RemoveField(
            model_name="child",
            name="annees_kt",
        ),
        migrations.RemoveField(
            model_name="child",
            name="pardon",
        ),
        migrations.RemoveField(
            model_name="child",
            name="redoublement",
        ),
        migrations.AddField(
            model_name="child",
            name="confirmation",
            field=models.BooleanField(default=False, verbose_name="Confirmation"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="child",
            name="date_confirmation",
            field=models.DateField(blank=True, null=True, verbose_name="Date de la Confirmation"),
        ),
        migrations.AddField(
            model_name="child",
            name="date_profession",
            field=models.DateField(blank=True, null=True, verbose_name="Date de la Profession de Foi"),
        ),
        migrations.AddField(
            model_name="child",
            name="lieu_confirmation",
            field=models.CharField(blank=True, max_length=100, verbose_name="Lieu de la Confirmation"),
        ),
        migrations.AddField(
            model_name="child",
            name="lieu_profession",
            field=models.CharField(blank=True, max_length=100, verbose_name="Lieu de la Profession de Foi"),
        ),
        migrations.AddField(
            model_name="child",
            name="profession",
            field=models.BooleanField(default=False, verbose_name="Profession de foi"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="child",
            name="ecole",
            field=models.CharField(max_length=100, verbose_name="École"),
        ),
    ]