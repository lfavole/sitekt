# Generated by Django 4.1.3 on 2022-12-07 18:37

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("espacecate", "0004_rename_id_page_slug_alter_page_content"),
    ]

    operations = [
        migrations.CreateModel(
            name="Child",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "last_name",
                    models.CharField(max_length=100, verbose_name="Nom de famille"),
                ),
                ("first_name", models.CharField(max_length=100, verbose_name="Prénom")),
                ("date_of_birth", models.DateField(verbose_name="Date de naissance")),
                (
                    "place_of_birth",
                    models.CharField(max_length=100, verbose_name="Lieu de naissance"),
                ),
                ("address", models.TextField(verbose_name="Adresse")),
                (
                    "school",
                    models.CharField(
                        choices=[
                            ("FARANDOLE", "École La Farandole"),
                            ("SOLDANELLE", "École La Soldanellle"),
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
                        ],
                        max_length=15,
                        verbose_name="École",
                    ),
                ),
                (
                    "level",
                    models.CharField(
                        choices=[
                            ("PS", "Petite section"),
                            ("MS", "Moyenne section"),
                            ("GS", "Grande section"),
                            ("CP", "CP"),
                            ("CE1", "CE1"),
                            ("CE2", "CE2"),
                            ("CM1", "CM1"),
                            ("CM2", "CM2"),
                        ],
                        max_length=5,
                        verbose_name="Classe",
                    ),
                ),
                ("redoublement", models.BooleanField(verbose_name="Redoublement")),
                (
                    "years_evf",
                    models.IntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(10000),
                        ],
                        verbose_name="Années d'éveil à la foi",
                    ),
                ),
                (
                    "years_kt",
                    models.IntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(10000),
                        ],
                        verbose_name="Années de caté",
                    ),
                ),
                ("bapteme", models.BooleanField(verbose_name="Baptême")),
                ("date_bapteme", models.DateField(verbose_name="Date du baptême")),
                (
                    "lieu_bapteme",
                    models.CharField(max_length=100, verbose_name="Lieu du baptême"),
                ),
                ("pardon", models.BooleanField(verbose_name="Sacrement du Pardon")),
                (
                    "annee_pardon",
                    models.IntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1970),
                            django.core.validators.MaxValueValidator(2022),
                        ],
                        verbose_name="Année du Sacrement du Pardon",
                    ),
                ),
                (
                    "premiere_communion",
                    models.BooleanField(verbose_name="première communion"),
                ),
                (
                    "date_premiere_communion",
                    models.DateField(verbose_name="Date de la première communion"),
                ),
                (
                    "lieu_premiere_communion",
                    models.CharField(
                        max_length=100, verbose_name="Lieu de la première communion"
                    ),
                ),
                (
                    "nom_pere",
                    models.CharField(
                        blank=True, max_length=100, verbose_name="Nom et prénom du père"
                    ),
                ),
                ("adresse_pere", models.TextField(verbose_name="Adresse du père")),
                (
                    "tel_pere",
                    models.TextField(max_length=10, verbose_name="Téléphone du père"),
                ),
                (
                    "email_pere",
                    models.EmailField(max_length=100, verbose_name="Email du père"),
                ),
                (
                    "nom_mere",
                    models.CharField(
                        blank=True,
                        max_length=100,
                        verbose_name="Nom et prénom de la mère",
                    ),
                ),
                ("adresse_mere", models.TextField(verbose_name="Adresse de la mère")),
                (
                    "tel_mere",
                    models.TextField(
                        max_length=10, verbose_name="Téléphone de la mère"
                    ),
                ),
                (
                    "email_mere",
                    models.EmailField(max_length=100, verbose_name="Email de la mère"),
                ),
                ("freres_soeurs", models.TextField(verbose_name="Frères et soeurs")),
                ("autres_infos", models.TextField(verbose_name="Autres informations")),
                ("photos", models.BooleanField(verbose_name="Publication des photos")),
                (
                    "frais",
                    models.IntegerField(
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Participation aux frais",
                    ),
                ),
            ],
        ),
    ]
