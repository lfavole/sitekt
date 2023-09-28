# Generated by Django 4.2.3 on 2023-09-27 12:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("aumonerie", "0025_article_id_page_id_alter_article_slug_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="attendance",
            name="child",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="attendances",
                related_query_name="attendance",
                to="aumonerie.child",
                verbose_name="Child",
            ),
        ),
        migrations.AlterField(
            model_name="attendance",
            name="meeting",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="attendances",
                related_query_name="attendance",
                to="aumonerie.meeting",
                verbose_name="Meeting",
            ),
        ),
    ]
