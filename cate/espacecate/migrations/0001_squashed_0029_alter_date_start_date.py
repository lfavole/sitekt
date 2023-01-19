# Generated by Django 4.1.3 on 2023-01-19 18:04

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import espacecate.models
import utils.fields
import uuid


class Migration(migrations.Migration):

    replaces = [
        ("espacecate", "0001_initial"),
        ("espacecate", "0002_rename_titre_page_title"),
        ("espacecate", "0003_article_alter_page_content_alter_page_id_and_more"),
        ("espacecate", "0004_rename_id_page_slug_alter_page_content"),
        ("espacecate", "0005_child"),
        ("espacecate", "0006_rename_address_child_adresse_and_more"),
        ("espacecate", "0007_rename_years_evf_child_annees_evf_and_more"),
        ("espacecate", "0008_rename_child_enfant"),
        ("espacecate", "0009_page_hidden_page_parent_page"),
        ("espacecate", "0010_alter_page_options_page_order"),
        ("espacecate", "0011_document_alter_page_order_alter_page_parent_page"),
        ("espacecate", "0012_alter_document_file"),
        ("espacecate", "0013_alter_document_file_delete_article"),
        ("espacecate", "0014_article"),
        ("espacecate", "0015_espacecateuservisit"),
        ("espacecate", "0016_alter_enfant_annees_evf_alter_enfant_annees_kt"),
        ("espacecate", "0017_rename_enfant_child_alter_child_options"),
        ("espacecate", "0018_remove_espacecateuservisit_hash"),
        ("espacecate", "0019_espacecateuservisit_hash"),
        (
            "espacecate",
            "0020_rename_espacecateuservisit_uservisit_and_more_squashed_0028_alter_document_file",
        ),
        ("espacecate", "0029_alter_date_start_date"),
    ]

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Page",
            fields=[
                (
                    "slug",
                    models.SlugField(
                        editable=False,
                        max_length=100,
                        primary_key=True,
                        serialize=False,
                        verbose_name="Slug",
                    ),
                ),
                ("title", models.CharField(max_length=100, verbose_name="Title")),
                ("content", models.TextField(blank=True, verbose_name="Content")),
                (
                    "hidden",
                    models.BooleanField(default=False, verbose_name="Hidden page"),
                ),
                (
                    "parent_page",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="espacecate.page",
                        verbose_name="Previous page",
                    ),
                ),
                ("order", models.PositiveIntegerField(default=0, verbose_name="Order")),
            ],
            options={
                "ordering": ["order"],
                "verbose_name": "page",
            },
        ),
        migrations.CreateModel(
            name="UserVisit",
            fields=[
                (
                    "uuid",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "timestamp",
                    models.DateTimeField(
                        default=django.utils.timezone.now, help_text="Time of the visit"
                    ),
                ),
                (
                    "session_key",
                    models.CharField(
                        help_text="Django session identifier", max_length=40
                    ),
                ),
                (
                    "remote_addr",
                    models.CharField(
                        blank=True,
                        help_text="Client IP address (from X-Forwarded-For HTTP header, or REMOTE_ADDR request property)",
                        max_length=100,
                    ),
                ),
                (
                    "ua_string",
                    models.TextField(
                        blank=True,
                        help_text="Client User-Agent HTTP header",
                        verbose_name="User agent (raw)",
                    ),
                ),
                (
                    "namespace",
                    models.CharField(
                        blank=True, help_text="View namespace", max_length=32
                    ),
                ),
                (
                    "view",
                    models.CharField(
                        blank=True, help_text="View name or object", max_length=32
                    ),
                ),
                (
                    "hash",
                    models.CharField(
                        default="",
                        help_text="MD5 hash generated from request properties",
                        max_length=32,
                    ),
                ),
            ],
            options={
                "verbose_name": "Visite",
                "verbose_name_plural": "Visites",
                "get_latest_by": "timestamp",
                "abstract": False,
            },
        ),
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
                    "nom",
                    models.CharField(max_length=100, verbose_name="Nom de famille"),
                ),
                ("prenom", models.CharField(max_length=100, verbose_name="Prénom")),
                ("date_naissance", models.DateField(verbose_name="Date de naissance")),
                (
                    "lieu_naissance",
                    models.CharField(max_length=100, verbose_name="Lieu de naissance"),
                ),
                ("adresse", models.TextField(verbose_name="Adresse")),
                (
                    "ecole",
                    models.CharField(
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
                        ],
                        max_length=15,
                        verbose_name="École",
                    ),
                ),
                (
                    "classe",
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
                    "annees_evf",
                    models.IntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(4),
                        ],
                        verbose_name="Années d'éveil à la foi",
                    ),
                ),
                (
                    "annees_kt",
                    models.IntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(3),
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
                            django.core.validators.MaxValueValidator(
                                espacecate.models.get_current_year
                            ),
                        ],
                        verbose_name="Année du Sacrement du Pardon",
                    ),
                ),
                (
                    "premiere_communion",
                    models.BooleanField(verbose_name="Première communion"),
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
                    models.CharField(max_length=10, verbose_name="Téléphone du père"),
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
                    models.CharField(
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
            options={
                "verbose_name": "Enfant",
            },
        ),
        migrations.CreateModel(
            name="Article",
            fields=[
                (
                    "slug",
                    models.SlugField(
                        editable=False,
                        max_length=100,
                        primary_key=True,
                        serialize=False,
                        verbose_name="Slug",
                    ),
                ),
                ("title", models.CharField(max_length=100, verbose_name="Title")),
                ("content", models.TextField(blank=True, verbose_name="Content")),
                (
                    "hidden",
                    models.BooleanField(default=False, verbose_name="Hidden article"),
                ),
                (
                    "date",
                    models.DateField(
                        default=django.utils.timezone.now, verbose_name="Date"
                    ),
                ),
            ],
            options={
                "abstract": False,
                "ordering": ["-date"],
                "verbose_name": "article",
            },
        ),
        migrations.CreateModel(
            name="Document",
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
                    "title",
                    models.CharField(max_length=100, verbose_name="Document title"),
                ),
                (
                    "file",
                    models.FileField(null=True, upload_to="", verbose_name="File"),
                ),
            ],
            options={
                "verbose_name": "document",
            },
        ),
        migrations.CreateModel(
            name="Date",
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
                ("start_time", models.TimeField(blank=True, verbose_name="Start time")),
                ("end_time", models.TimeField(blank=True, verbose_name="End time")),
                (
                    "time_text",
                    utils.fields.DatalistField(
                        blank=True, max_length=50, verbose_name="Time (as text)"
                    ),
                ),
                ("name", models.CharField(max_length=100, verbose_name="Name")),
                (
                    "short_name",
                    models.CharField(
                        blank=True, max_length=50, verbose_name="Short name"
                    ),
                ),
                ("place", models.CharField(max_length=100, verbose_name="Place")),
                ("cancelled", models.BooleanField(verbose_name="Cancelled")),
                ("end_date", models.DateField(blank=True, verbose_name="End date")),
                ("start_date", models.DateField(verbose_name="Start date")),
            ],
            options={
                "verbose_name": "date",
                "abstract": False,
            },
        ),
    ]
