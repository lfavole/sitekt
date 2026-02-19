from datetime import timedelta
from django.utils.timezone import now
from django.contrib.messages import add_message
from django.contrib.messages.constants import INFO
from django.utils.safestring import mark_safe

from .models import Date


class EventInProgressMiddleware:
    """Middleware that adds a permanent info message when an event is in progress.

    Shows a message between 1 hour before the event start and 30 minutes after the
    event end. The message contains a Google Maps directions link when latitude/longitude
    are available.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # compute once per request
        self.process_request(request)
        return self.get_response(request)

    def process_request(self, request):
        now_dt = now()
        # look for dates that are not cancelled
        dates = Date.objects.filter(cancelled=False)
        for d in dates:
            try:
                start = d.start
                end = d.end
            except Exception:
                continue

            window_start = (start - timedelta(hours=1)) if hasattr(start, 'tzinfo') or True else start
            window_end = end + timedelta(minutes=30)

            # compare aware datetimes or dates
            in_window = False
            if hasattr(start, 'hour') and hasattr(now_dt, 'hour'):
                # start/end are datetimes
                in_window = window_start <= now_dt <= window_end
            else:
                # date-only, compare dates
                in_window = (start <= now_dt.date() <= end)

            if in_window:
                # build link
                if d.latitude is not None and d.longitude is not None:
                    dest = f"{d.latitude},{d.longitude}"
                    maps_url = f"https://www.google.com/maps/dir/?api=1&destination={dest}"
                elif d.place:
                    maps_url = (
                        "https://www.google.com/maps/dir/?api=1&destination=" +
                        d.place.replace(' ', '+')
                    )
                else:
                    maps_url = ""

                if maps_url:
                    msg = mark_safe(
                        f"L'événement '<strong>{d.name}</strong>' est en cours — "
                        f"<a href=\"{maps_url}\" target=\"_blank\">Itinéraire</a>"
                    )
                else:
                    msg = f"L'événement '{d.name}' est en cours."

                # add a message with a specific tag so template can render it as safe
                add_message(request, INFO, msg, extra_tags='event')
                # only show first matching event
                break
