from common.admin import (
    CommonAttendancesInline,
    CommonChildAdmin,
    CommonMeetingAdmin,
    OldChildMixin,
)
from django.contrib import admin

from .models import (
    Attendance,
    Child,
    Meeting,
    OldChild,
)


@admin.register(Child)
class ChildAdmin(CommonChildAdmin):
    """
    Admin interface for childs of the espacecate app.
    """

    other_model = OldChild
    list_display = ("nom", "prenom", "classe", "paye", "signe", "groupe")
    readonly_fields = ("date_inscription",)
    search_fields = ("nom", "prenom")
    list_filter = (
        "groupe",
        "communion_cette_annee",
        "paye",
        "signe",
        "classe",
        "bapteme",
        "premiere_communion",
        "photos",
    )


@admin.register(OldChild)
class OldChildAdmin(OldChildMixin, CommonChildAdmin):
    """
    Admin interface for old children of the espacecate app.
    """
    other_model = Child


class AttendancesInline(CommonAttendancesInline):
    """
    Inline for attendances of the espacecate app.
    """

    model = Attendance


@admin.register(Meeting)
class MeetingAdmin(CommonMeetingAdmin):
    """
    Admin interface for meetings of the espacecate app.
    """

    inlines = [AttendancesInline]
