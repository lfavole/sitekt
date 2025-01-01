from datetime import datetime

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
)
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Article(CommonArticle):
    """
    Article on `espacecate` app.
    """

    def get_absolute_url(self):
        return reverse("espacecate:article", args=[self.slug])


class ArticleImage(CommonArticleImage):
    """
    Article image on `espacecate` app.
    """


def get_current_year():
    return datetime.now().year


class Group(CommonGroup):
    """
    Group on `espacecate` app.
    """


class Child(CommonChild):
    """
    A subscribed child.
    """

    class Classes(models.TextChoices):
        PS = "PS", "Petite section"
        MS = "MS", "Moyenne section"
        GS = "GS", "Grande section"
        CP = "CP", "CP"
        CE1 = "CE1", "CE1"
        CE2 = "CE2", "CE2"
        CM1 = "CM1", "CM1"
        CM2 = "CM2", "CM2"
        AUTRE = "autre", "Autre"

        def __lt__(self, other):
            return self._sort_order_ < other._sort_order_

    classe = models.fields.TextField("Classe", choices=Classes.choices, max_length=5)

    communion_cette_annee = models.BooleanField("Communion cette année", default=False)

    fieldsets = [
        *CommonChild.fieldsets,
        (
            "Espace administrateur",
            {"fields": ("communion_cette_annee", *CommonChild.admin_fields)},
        ),
    ]

    sacraments_checks = {
        "bapteme": "du baptême",
        "pardon": "du Sacrement du Pardon",
        "premiere_communion": "de la première communion",
    }


class Date(CommonDate):
    """
    Date on `espacecate` app.
    """


class Meeting(CommonMeeting):
    """
    Meeting on `espacecate` app.
    """

    class Kind(models.TextChoices):
        CATE = "KT", "Rencontre de caté"
        EVF = "EVF", "Rencontre d'éveil à la foi"
        TEMPS_FORT = "TF", "Temps fort"
        MESSE_FAMILLES = "MF", "Messe des familles"

    kind = models.CharField(_("kind"), max_length=5, blank=True, choices=Kind.choices)

    def get_childs(self):
        """
        Returns all the `Childs` that match the kind of this `Meeting`.
        """
        kind = self.kind
        objs = Child.objects.all()

        if kind == Meeting.Kind.CATE:
            groups_ok = ["Giang", "Eliane", "Carine"]
            return objs.filter(groupe__name__in=groups_ok)

        if kind == Meeting.Kind.EVF:
            return objs.filter(groupe__name="EVF")

        return objs


class Attendance(CommonAttendance):
    """
    Attendance on `espacecate` app.
    """


class DocumentCategory(CommonDocumentCategory):
    """
    Document category on `espacecate` app.
    """


class Document(CommonDocument):
    """
    Document on `espacecate` app.
    """
