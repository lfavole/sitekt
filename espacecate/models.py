import datetime

from common.models import (
    Attendance as CommonAttendance,
    Child as CommonChild,
    ChildManager,
    items_for,
    Meeting as CommonMeeting,
    OldChildManager,
)
from django.utils.translation import gettext_lazy as _

def get_current_year():
    return datetime.date.today().year


class Child(CommonChild):
    """
    A subscribed child.
    """
    objects = items_for("espacecate", ChildManager)

    sacraments_checks = {
        "bapteme": "du baptême",
        "premiere_communion": "de la première communion",
    }

    class Meta:
        verbose_name = _("child")
        verbose_name_plural = _("children")
        proxy = True


class OldChild(Child):
    """
    Old child on `espacecate` app.
    """

    objects = items_for("espacecate", OldChildManager)

    class Meta:
        verbose_name = _("old child")
        verbose_name_plural = _("old children")
        proxy = True


class Meeting(CommonMeeting):
    """
    Meeting on `espacecate` app.
    """
    objects = items_for("espacecate")

    class Meta:
        proxy = True


class Attendance(CommonAttendance):
    """
    Attendance on `espacecate` app.
    """
    objects = items_for("espacecate")

    class Meta:
        proxy = True
