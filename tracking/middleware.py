import datetime as dt
import re
import warnings
from typing import Callable

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.utils import timezone
from django.utils.encoding import smart_str

from .models import PageView, Visit
from .settings import (
    MAX_VISIT_TIME,
    TRACK_AJAX_REQUESTS,
    TRACK_ANONYMOUS_USERS,
    TRACK_IGNORE_STATUS_CODES,
    TRACK_IGNORE_URLS,
    TRACK_IGNORE_USER_AGENTS,
    TRACK_PAGEVIEWS,
    TRACK_QUERY_STRING,
    TRACK_REFERER,
    TRACK_SUPERUSERS,
)
from .utils import get_ip_address

track_ignore_urls = [re.compile(x) for x in TRACK_IGNORE_URLS]
track_ignore_user_agents = [re.compile(x, re.IGNORECASE) for x in TRACK_IGNORE_USER_AGENTS]


class VisitTrackingMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response = self.process_response(request, response)
        return response

    def _should_track(self, request: HttpRequest, response: HttpResponse):
        # Session framework not installed, nothing to see here...
        if not hasattr(request, "session"):
            warnings.warn("VisitTrackingMiddleware installed without SessionMiddleware", RuntimeWarning)
            return False

        # Do not track AJAX requests
        if request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest" and not TRACK_AJAX_REQUESTS:
            return False

        # Do not track if HTTP HttpResponse status_code blacklisted
        if response.status_code in TRACK_IGNORE_STATUS_CODES:
            return False

        # Do not track anonymous users if set
        if getattr(request, "user", None) and request.user.is_anonymous and not TRACK_ANONYMOUS_USERS:
            return False
        # If dealing with a non-authenticated user, we still should track the
        # session since if authentication happens, the `session_key` carries
        # over, thus having a more accurate start time of session

        # Do not track superusers if set
        if getattr(request, "user", None) and request.user.is_superuser and not TRACK_SUPERUSERS:
            return False

        # Do not track ignored urls
        path = request.path_info.lstrip("/")
        for url in track_ignore_urls:
            if url.match(path):
                return False

        # Do not track ignored user agents
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        for user_agent_pattern in track_ignore_user_agents:
            if user_agent_pattern.match(user_agent):
                return False

        # everything says we should track this hit
        return True

    def _refresh_visit(self, request: HttpRequest, visit_time: dt.datetime):
        # A Visit row is unique by session_key
        session_key = request.session.session_key

        visit = None
        last_access_ts = request.session.get("last_access_ts")

        if last_access_ts is not None:
            last_access = dt.datetime.fromtimestamp(last_access_ts, tz=dt.timezone.utc if settings.USE_TZ else None)
            if (visit_time - last_access) <= MAX_VISIT_TIME:
                try:
                    visit = Visit.objects.filter(session_key=session_key).first()
                except Visit.DoesNotExist:
                    pass

        # Save the last access timestamp
        request.session["last_access_ts"] = visit_time.timestamp()

        if visit is None:
            # Log the ip address. Start time is managed via the field
            # `default` value
            ip_address = get_ip_address(request)
            visit = Visit(session_key=session_key, ip_address=ip_address)

        # Update the user field if the visit user is not set.
        # This implies authentication has occured on this request and now the user is object exists.
        # Check using `user_id` to prevent a database hit.
        if getattr(request, "user", None) and not visit.user_id:  # type: ignore
            visit.user_id = request.user.id  # type: ignore

        # update session expiration time
        visit.expiry_time = request.session.get_expiry_date()

        # grab the latest User-Agent and store it
        user_agent = request.META.get("HTTP_USER_AGENT", None)
        if user_agent:
            visit.user_agent = smart_str(user_agent, encoding="latin-1", errors="ignore")

        time_on_site = 0
        if visit.start_time:
            time_on_site = (visit_time - visit.start_time).total_seconds()
        visit.time_on_site = int(time_on_site)

        visit.save()

        return visit

    def _add_pageview(self, visit, request, view_time):
        PageView.objects.create(
            visit=visit,
            url=request.path,
            view_time=view_time,
            method=request.method,
            referer=request.META.get("HTTP_REFERER", "") if TRACK_REFERER else "",
            query_string=request.META.get("QUERY_STRING", "") if TRACK_QUERY_STRING else "",
        )

    def process_response(self, request: HttpRequest, response: HttpResponse):
        # make sure this is a response we want to track
        if not self._should_track(request, response):
            return response

        # Force a save to generate a session key if one does not exist
        if not request.session.session_key:
            request.session.save()

        # Be conservative with the determining time on site since simply
        # increasing the session timeout could greatly skew results. This
        # is the only time we can guarantee.
        now = timezone.now()

        # update/create the visit object for this request
        visit = self._refresh_visit(request, now)

        if TRACK_PAGEVIEWS:
            self._add_pageview(visit, request, now)

        return response
