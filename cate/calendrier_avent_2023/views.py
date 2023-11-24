from datetime import date

from django.http import Http404, HttpRequest
from django.shortcuts import render

from common.views import has_permission

from .models import Day

DAYS = 25
MONTH = 12
YEAR = 2023
start = date(YEAR, MONTH, 1)
end = date(YEAR, MONTH, 25)


def home(request: HttpRequest):
    today = date.today()
    return render(
        request,
        "calendrier_avent_2023/home.html",
        {"days": range(1, DAYS + 1), "today": today.day if start <= today <= end else -1},
    )


def day(request, day: int):
    has_perm = has_permission(request, Day)
    today = date.today()
    day_date = date(YEAR, MONTH, day)

    try:
        day_obj = Day.objects.get(day=day)
    except Day.DoesNotExist:
        day_obj = None  # hide the 404 error if too early (see below)

    if today < day_date and (not has_perm or not bool(request.GET.get("unlock"))):
        return render(
            request,
            "calendrier_avent_2023/too_early.html",
            {
                "day_obj": day_obj,
                "day": day,
                "not_begun": today < start,
                "date_to_wait": start if today < start else day_date,
                "has_perm": has_perm,
            },
        )

    if day_obj is None:
        raise Http404
    return render(request, "calendrier_avent_2023/day.html", {"day": day_obj})
