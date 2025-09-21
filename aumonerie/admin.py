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
    Admin interface for childs of the aumonerie app.
    """

    other_model = OldChild


@admin.register(OldChild)
class OldChildAdmin(OldChildMixin, CommonChildAdmin):
    """
    Admin interface for old children of the aumonerie app.
    """
    other_model = Child


class AttendancesInline(CommonAttendancesInline):
    """
    Inline for attendances of the aumonerie app.
    """

    model = Attendance


@admin.register(Meeting)
class MeetingAdmin(CommonMeetingAdmin):
    """
    Admin interface for meetings of the aumonerie app.
    """

    inlines = [AttendancesInline]
