from datetime import timedelta

from django import forms
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from django.utils.timezone import now

from .models import PageView, Visit
from .settings import TRACK_PAGEVIEWS

# tracking wants to accept more formats than default, here they are
input_formats = [
    "%Y-%m-%d %H:%M:%S",    # "2006-10-25 14:30:59"
    "%Y-%m-%d %H:%M",       # "2006-10-25 14:30"
    "%Y-%m-%d",             # "2006-10-25"
    "%Y-%m",                # "2006-10"
    "%Y",                   # "2006"
]


class DashboardForm(forms.Form):
    start = forms.DateTimeField(required = False, input_formats = input_formats)
    end = forms.DateTimeField(required = False, input_formats = input_formats)


@permission_required("tracking.visitor_log")
def dashboard(request):
    """
    Counts, aggregations and more!
    """
    end_time = now()
    start_time = end_time - timedelta(days = 7)
    defaults = {"start": start_time, "end": end_time}

    form = DashboardForm(data = request.GET or defaults)
    if form.is_valid():
        start_time = form.cleaned_data["start"]
        end_time = form.cleaned_data["end"]

    # determine when tracking began
    try:
        obj = Visit.objects.order_by("start_time")[0]
        track_start_time = obj.start_time
    except (IndexError, Visit.DoesNotExist):
        track_start_time = now()

    # If the start_date is before tracking began, warn about incomplete data
    warn_incomplete = (start_time < track_start_time)

    # queries take `date` objects (for now)
    user_stats = Visit.objects.user_stats(start_time, end_time)
    visitor_stats = Visit.objects.stats(start_time, end_time)
    if TRACK_PAGEVIEWS:
        pageview_stats = PageView.objects.stats(start_time, end_time)
    else:
        pageview_stats = None

    context = {
        "form": form,
        "track_start_time": track_start_time,
        "warn_incomplete": warn_incomplete,
        "user_stats": user_stats,
        "visitor_stats": visitor_stats,
        "pageview_stats": pageview_stats,
    }
    return render(request, "tracking/dashboard.html", context)
