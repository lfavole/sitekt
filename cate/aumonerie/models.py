from common.fields import PriceField
from common.models import (
    CommonArticle,
    CommonArticleImage,
    CommonAttendance,
    CommonChild,
    CommonDate,
    CommonDocument,
    CommonDocumentCategory,
    CommonGroup,
    CommonMeeting,
    CommonPage,
    CommonPageImage,
)
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Page(CommonPage):
    """
    Page on `aumonerie` app.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("aumonerie:page", args=[self.slug])


class PageImage(CommonPageImage):
    """
    Page image on `aumonerie` app.
    """


class Article(CommonArticle):
    """
    Article on `aumonerie` app.
    """

    def get_absolute_url(self):
        return reverse("aumonerie:article", args=[self.slug])


class ArticleImage(CommonArticleImage):
    """
    Article image on `aumonerie` app.
    """


class Group(CommonGroup):
    """
    Group on `aumonerie` app.
    """


class Child(CommonChild):
    """
    A subscribed child.
    """

    CLASSES = [
        ("6e", "6ème"),
        ("5e", "5ème"),
        ("4e", "4ème"),
        ("3e", "3ème"),
        ("2nde", "2nde"),
        ("1ere", "1ère"),
        ("terminale", "Terminale"),
        ("AUTRE", "Autre"),
    ]

    ecole = models.fields.CharField("École", max_length=100)
    classe = models.fields.CharField("Classe", choices=CLASSES, max_length=10)

    bapteme = models.fields.BooleanField("Baptême")
    date_bapteme = models.fields.DateField("Date du Baptême", blank=True, null=True)
    lieu_bapteme = models.CharField("Lieu du Baptême", max_length=100, blank=True)

    premiere_communion = models.fields.BooleanField("Première Communion")
    date_premiere_communion = models.fields.DateField("Date de la Première Communion", blank=True, null=True)
    lieu_premiere_communion = models.CharField("Lieu de la Première Communion", max_length=100, blank=True)

    profession = models.fields.BooleanField("Profession de foi")
    date_profession = models.fields.DateField("Date de la Profession de Foi", blank=True, null=True)
    lieu_profession = models.CharField("Lieu de la Profession de Foi", max_length=100, blank=True)

    confirmation = models.fields.BooleanField("Confirmation")
    date_confirmation = models.fields.DateField("Date de la Confirmation", blank=True, null=True)
    lieu_confirmation = models.CharField("Lieu de la Confirmation", max_length=100, blank=True)

    nom_pere = models.CharField("Nom et prénom du père", blank=True, max_length=100)
    adresse_pere = models.TextField("Adresse du père", blank=True)
    tel_pere = models.CharField("Téléphone du père", blank=True, max_length=10)
    email_pere = models.EmailField("Email du père", blank=True, max_length=100)

    nom_mere = models.CharField("Nom et prénom de la mère", blank=True, max_length=100)
    adresse_mere = models.TextField("Adresse de la mère", blank=True)
    tel_mere = models.CharField("Téléphone de la mère", blank=True, max_length=10)
    email_mere = models.EmailField("Email de la mère", blank=True, max_length=100)

    freres_soeurs = models.TextField("Frères et soeurs", blank=True)

    autres_infos = models.TextField("Autres informations", blank=True)

    photos = models.BooleanField("Publication des photos")
    frais = PriceField("Participation aux frais")

    profession_cette_annee = models.BooleanField("Profession de Foi cette année")
    confirmation_cette_annee = models.BooleanField("Confirmation cette année")

    fieldsets = [
        (
            "Informations concernant le jeune",
            {"fields": ("nom", "prenom", "date_naissance", "lieu_naissance", "adresse")},
        ),
        ("École", {"fields": ("ecole", "classe")}),
        (
            "Aumônerie",
            {
                "fields": (
                    "bapteme",
                    "date_bapteme",
                    "lieu_bapteme",
                    "premiere_communion",
                    "date_premiere_communion",
                    "lieu_premiere_communion",
                    "profession",
                    "date_profession",
                    "lieu_profession",
                    "confirmation",
                    "date_confirmation",
                    "lieu_confirmation",
                )
            },
        ),
        (
            "Coordonnées",
            {
                "fields": (
                    "nom_mere",
                    "adresse_mere",
                    "tel_mere",
                    "email_mere",
                    "nom_pere",
                    "adresse_pere",
                    "tel_pere",
                    "email_pere",
                    "freres_soeurs",
                )
            },
        ),
        ("Autres informations", {"fields": ("autres_infos",)}),
        ("Autorisation", {"fields": ("photos", "frais")}),
        (
            "Espace administrateur",
            {
                "fields": (
                    "profession_cette_annee",
                    "confirmation_cette_annee",
                    "paye",
                    "signe",
                    "groupe",
                    "photo",
                    "date_inscription",
                )
            },
        ),
    ]

    sacraments_checks = {
        "bapteme": "du baptême",
        "premiere_communion": "de la première communion",
        "profession": "de la profession de foi",
        "confirmation": "de la Confirmation",
    }


class Date(CommonDate):
    """
    Date on `aumonerie` app.
    """


class Meeting(CommonMeeting):
    """
    Meeting on `aumonerie` app.
    """

    class Kind(models.TextChoices):
        AUMONERIE_COLLEGE = "A_COL", "Rencontre d'aumônerie (collège)"
        AUMONERIE_LYCEE = "A_LYC", "Rencontre d'aumônerie (lycée)"
        MESSE_FAMILLES = "MF", "Messe des familles"
        PROFESSION = "PF", "Profession de Foi"
        CONFIRMATION = "CONF", "Confirmation"

    kind = models.CharField(_("kind"), max_length=5, blank=True, choices=Kind.choices)

    def get_childs(self):
        """
        Returns all the `Childs` that match the kind of this `Meeting`.
        """
        kind = self.kind
        objs = Child.objects.all()

        if kind == Meeting.Kind.AUMONERIE_COLLEGE:
            return objs.filter(groupe__name="Collège")

        if kind == Meeting.Kind.AUMONERIE_LYCEE:
            return objs.filter(groupe__name="Lycée")

        if kind == Meeting.Kind.PROFESSION:
            return objs.filter(profession_cette_annee=True)

        if kind == Meeting.Kind.CONFIRMATION:
            return objs.filter(confirmation_cette_annee=True)

        return objs


class Attendance(CommonAttendance):
    """
    Attendance on `aumonerie` app.
    """


class DocumentCategory(CommonDocumentCategory):
    """
    Document category on `aumonerie` app.
    """


class Document(CommonDocument):
    """
    Document on `aumonerie` app.
    """
