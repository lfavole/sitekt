# Generated by Django 4.2.3 on 2023-08-16 12:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("espacecate", "0018_alter_date_options_alter_child_signe"),
    ]

    operations = [
        migrations.AlterField(
            model_name="child",
            name="classe",
            field=models.CharField(
                choices=[
                    ("PS", "Petite section"),
                    ("MS", "Moyenne section"),
                    ("GS", "Grande section"),
                    ("CP", "CP"),
                    ("CE1", "CE1"),
                    ("CE2", "CE2"),
                    ("CM1", "CM1"),
                    ("CM2", "CM2"),
                    ("AUTRE", "Autre"),
                ],
                max_length=5,
                verbose_name="Classe",
            ),
        ),
        migrations.AlterField(
            model_name="child",
            name="ecole",
            field=models.CharField(
                choices=[
                    ("FARANDOLE", "École La Farandole"),
                    ("SOLDANELLE", "École La Soldanelle"),
                    ("PASTEUR", "École Pasteur"),
                    ("CEZANNE", "École Cézanne"),
                    ("BARATIER", "École de Baratier"),
                    ("CHATEAUROUX", "École de Châteauroux"),
                    ("ST_ANDRE", "École de Saint-André"),
                    ("CROTS", "École de Crots"),
                    ("SAVINES", "École de Savines"),
                    ("ORRES", "École des Orres"),
                    ("PUYS", "École des Puys"),
                    ("MAISON", "École à la maison"),
                    ("AUTRE", "Autre"),
                ],
                max_length=15,
                verbose_name="École",
            ),
        ),
    ]
