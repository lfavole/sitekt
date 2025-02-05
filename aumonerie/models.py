from common.models import (
    ClassesMixin,
    CommonArticle,
    CommonArticleImage,
    CommonAttendance,
    CommonChild,
    CommonDate,
    CommonDocument,
    CommonDocumentCategory,
    CommonGroup,
    CommonMeeting,
    OldChildManager,
)
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Article(CommonArticle):
    """
    Article on `aumonerie` app.
    """

    def get_absolute_url(self):
        return reverse("aumonerie_article", args=[self.slug])


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

    class Classes(ClassesMixin, models.TextChoices):
        SIXIEME = "6eme", "6ème"
        CINQUIEME = "5eme", "5ème"
        QUATRIEME = "4eme", "4ème"
        TROISIEME = "3eme", "3ème"
        SECONDE = "2nde", "2nde"
        PREMIERE = "1ere", "1ère"
        TERMINALE = "terminale", "Terminale"
        AUTRE = "autre", "Autre"

        def __lt__(self, other):
            return self._sort_order_ < other._sort_order_

    classe = models.fields.TextField("Classe", choices=Classes.choices, max_length=10)

    profession_cette_annee = models.BooleanField("Profession de Foi cette année", default=False)
    confirmation_cette_annee = models.BooleanField("Confirmation cette année", default=False)

    fieldsets = [
        *CommonChild.fieldsets,
        (
            "Espace administrateur",
            {
                "fields": (
                    "profession_cette_annee",
                    "confirmation_cette_annee",
                    *CommonChild.admin_fields,
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


class OldChild(Child):
    """
    Old child on `aumonerie` app.
    """

    objects = OldChildManager()

    class Meta:
        verbose_name = _("old child")
        verbose_name_plural = _("old children")
        proxy = True


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
