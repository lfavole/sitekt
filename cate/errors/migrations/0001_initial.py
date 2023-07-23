# Generated by Django 4.2 on 2023-05-26 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Error',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(auto_now_add=True, verbose_name='time')),
                ('error_class', models.CharField(max_length=50, verbose_name='error class')),
                ('message', models.CharField(max_length=150, verbose_name='error message')),
                ('url', models.CharField(max_length=150, verbose_name='URL')),
                ('content', models.TextField(editable=False, verbose_name='HTML content')),
            ],
            options={
                'verbose_name': 'error',
                'ordering': ('-time',),
            },
        ),
    ]