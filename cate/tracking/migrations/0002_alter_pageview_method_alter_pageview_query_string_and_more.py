# Generated by Django 4.2.3 on 2023-09-30 06:40

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("tracking", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pageview",
            name="method",
            field=models.CharField(max_length=10, verbose_name="method"),
        ),
        migrations.AlterField(
            model_name="pageview",
            name="query_string",
            field=models.TextField(verbose_name="query string"),
        ),
        migrations.AlterField(
            model_name="pageview",
            name="referer",
            field=models.TextField(verbose_name="referer"),
        ),
        migrations.AlterField(
            model_name="pageview",
            name="view_time",
            field=models.DateTimeField(verbose_name="view time"),
        ),
        migrations.AlterField(
            model_name="visit",
            name="expiry_time",
            field=models.DateTimeField(verbose_name="session expiry time"),
        ),
        migrations.AlterField(
            model_name="visit",
            name="session_key",
            field=models.CharField(max_length=40, verbose_name="session key"),
        ),
        migrations.AlterField(
            model_name="visit",
            name="start_time",
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name="start time"),
        ),
        migrations.AlterField(
            model_name="visit",
            name="time_on_site",
            field=models.IntegerField(verbose_name="time on site"),
        ),
        migrations.AlterField(
            model_name="visit",
            name="user_agent",
            field=models.TextField(verbose_name="user agent"),
        ),
    ]
