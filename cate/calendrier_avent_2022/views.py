from datetime import date

from django.http import HttpRequest
from django.shortcuts import render
from django.views import generic

from .models import Day

DAYS = 25
today = lambda: date.today().day


def home(request: HttpRequest):
    return render(request, "calendrier_avent_2022/home.html", {"days": range(1, DAYS + 1), "today": today()})


class DayView(generic.DetailView):
    model = Day
    context_object_name = "day"
    template_name = "calendrier_avent_2022/day.html"
    pk_url_kwarg = "day"
    queryset = Day.objects.filter(day__gte=today())
