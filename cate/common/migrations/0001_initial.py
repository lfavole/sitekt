# Generated by Django 4.1.3 on 2023-02-09 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Year',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_year', models.IntegerField(unique=True, verbose_name='Start year')),
                ('is_active', models.BooleanField(verbose_name='Active year')),
            ],
            options={
                'verbose_name': 'school year',
                'ordering': ['-start_year'],
            },
        ),
    ]
