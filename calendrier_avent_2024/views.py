from datetime import date

from django.http import Http404, HttpRequest
from django.shortcuts import redirect, render

from common.views import has_permission

from .forms import SetDateForm
from .models import Day

DAYS = 25
MONTH = 12
YEAR = 2024
start = date(YEAR, MONTH, 1)
end = date(YEAR, MONTH, 25)


def home(request: HttpRequest):
    today = get_today(request)
    return render(
        request,
        "calendrier_avent_2024/home.html",
        {
            "days": range(1, DAYS + 1),
            "today": today.day if start <= today <= end else -1,
            "has_perm": has_permission(request, Day),
            "changed_date": request.session.get("date"),
        },
    )


def get_today(request: HttpRequest):
    if has_permission(request, Day) and "date" in request.session:
        try:
            return date.fromisoformat(request.session["date"])
        except ValueError:
            pass
    return date.today()


def set_date(request: HttpRequest):
    if not has_permission(request, Day):
        raise Http404
    if request.method == "POST":
        if request.POST.get("action") == "Supprimer":
            del request.session["date"]
            return redirect("calendrier_avent_2024:home")
        form = SetDateForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            request.session["date"] = str(data["new_date"])
            return redirect("calendrier_avent_2024:home")
    else:
        form = SetDateForm({"new_date": request.session["date"]} if "date" in request.session else None)
    return render(
        request,
        "calendrier_avent_2024/set_date.html",
        {
            "form": form,
            "changed_date": request.session.get("date"),
        },
    )


def day(request, day: int):
    has_perm = has_permission(request, Day)
    today = get_today(request)
    day_date = date(YEAR, MONTH, day)

    try:
        day_obj = Day.objects.get(day=day)
    except Day.DoesNotExist:
        day_obj = None  # hide the 404 error if too early (see below)

    if today < day_date and (not has_perm or not bool(request.GET.get("unlock"))):
        return render(
            request,
            "calendrier_avent_2024/too_early.html",
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
    return render(request, "calendrier_avent_2024/day.html", {"day": day_obj})
