# Generated by Django 5.1.4 on 2024-12-10 18:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("aumonerie", "0002_alter_page_parent_page"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="pageimage",
            name="page",
        ),
        migrations.DeleteModel(
            name="Page",
        ),
        migrations.DeleteModel(
            name="PageImage",
        ),
    ]
