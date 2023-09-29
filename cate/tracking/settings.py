from datetime import timedelta

from django.conf import settings

MAX_VISIT_TIME = getattr(settings, "MAX_VISIT_TIME", timedelta(seconds=1800))
if not isinstance(MAX_VISIT_TIME, timedelta):
    MAX_VISIT_TIME = timedelta(seconds=MAX_VISIT_TIME)

TRACK_AJAX_REQUESTS = getattr(settings, "TRACK_AJAX_REQUESTS", False)
TRACK_ANONYMOUS_USERS = getattr(settings, "TRACK_ANONYMOUS_USERS", True)
TRACK_SUPERUSERS = getattr(settings, "TRACK_SUPERUSERS", True)
TRACK_PAGEVIEWS = getattr(settings, "TRACK_PAGEVIEWS", False)

TRACK_IGNORE_URLS = getattr(settings, "TRACK_IGNORE_URLS", (r"^(favicon\.ico|robots\.txt)$",))
TRACK_IGNORE_USER_AGENTS = getattr(settings, "TRACK_IGNORE_USER_AGENTS", ())
TRACK_IGNORE_STATUS_CODES = getattr(settings, "TRACK_IGNORE_STATUS_CODES", ())

TRACK_REFERER = getattr(settings, "TRACK_REFERER", True)
TRACK_QUERY_STRING = getattr(settings, "TRACK_QUERY_STRING", True)
