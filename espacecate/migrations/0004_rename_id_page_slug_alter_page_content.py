# Generated by Django 4.1.3 on 2022-12-07 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("espacecate", "0003_article_alter_page_content_alter_page_id_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="page",
            old_name="id",
            new_name="slug",
        ),
        migrations.AlterField(
            model_name="page",
            name="content",
            field=models.TextField(blank=True, verbose_name="Contenu"),
        ),
    ]
