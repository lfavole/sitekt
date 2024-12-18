# Generated by Django 4.2.6 on 2023-11-01 13:48

from django.db import migrations, models
import storage.fields


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Day",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("day", models.IntegerField(unique=True, verbose_name="jour")),
                ("child", models.CharField(max_length=100, verbose_name="enfant")),
                ("picture", storage.fields.ImageField(null=True, upload_to="", verbose_name="photo")),
                ("character", models.CharField(max_length=100, verbose_name="personnage")),
                ("content", models.TextField(blank=True, verbose_name="contenu")),
            ],
            options={
                "verbose_name": "Jour",
            },
        ),
    ]