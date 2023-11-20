from datetime import date

from django.http import Http404, HttpRequest
from django.shortcuts import render

from .models import Day

DAYS = 25
MONTH = 11
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
    today = date.today()
    day_date = date(YEAR, MONTH, day)

    all_days = Day.objects.all()
    if today < start:
        all_days = all_days.none()
    if today <= end:
        all_days = all_days.filter(day__lte=today.day)

    try:
        day_obj = all_days.get(day=day)
    except Day.DoesNotExist:
        day_obj = None  # hide the 404 error if too early (see below)

    if today < day_date:
        return render(
            request,
            "calendrier_avent_2023/too_early.html",
            {
                "day_obj": day_obj,
                "day": day,
                "not_begun": today < start,
                "date_to_wait": start if today < start else day_date,
            },
        )

    if day_obj is None:
        raise Http404
    return render(request, "calendrier_avent_2023/day.html", {"day": day_obj})
