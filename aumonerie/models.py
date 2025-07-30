from common.models import (
    Attendance as CommonAttendance,
    Child as CommonChild,
    ChildManager,
    items_for,
    Meeting as CommonMeeting,
    OldChildManager,
)
from django.utils.translation import gettext_lazy as _


class Child(CommonChild):
    """
    A subscribed child.
    """
    objects = items_for("aumonerie", ChildManager)

    sacraments_checks = {
        "bapteme": "du baptême",
        "premiere_communion": "de la première communion",
        "profession": "de la profession de foi",
        "confirmation": "de la Confirmation",
    }

    class Meta:
        verbose_name = _("child")
        verbose_name_plural = _("children")
        proxy = True


class OldChild(CommonChild):
    """
    Old child on `aumonerie` app.
    """

    objects = items_for("aumonerie", OldChildManager)

    class Meta:
        verbose_name = _("old child")
        verbose_name_plural = _("old children")
        proxy = True


class Meeting(CommonMeeting):
    """
    Meeting on `aumonerie` app.
    """
    objects = items_for("aumonerie")

    class Meta:
        proxy = True


class Attendance(CommonAttendance):
    """
    Attendance on `aumonerie` app.
    """
    objects = items_for("aumonerie")

    class Meta:
        proxy = True
