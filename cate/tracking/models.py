from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import PageviewManager, VisitorManager


class Visit(models.Model):
    session_key = models.CharField(_("Session key"), max_length = 40)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name = "visit_history",
        null = True,
        editable = False,
        on_delete = models.SET_NULL,
        verbose_name = _("User"),
    )
    ip_address = models.GenericIPAddressField(_("IP address"))
    user_agent = models.TextField(_("User agent"))
    start_time = models.DateTimeField(_("Start time"), default = timezone.now)
    expiry_time = models.DateTimeField(_("Session expiry time"))
    time_on_site = models.IntegerField(_("Time on site"))

    objects = VisitorManager["Visit"]()

    class Meta(object):
        verbose_name = _("visit")
        ordering = ("-start_time",)
        permissions = (
            ("visitor_log", "Can view visitor"),
        )

    def session_expired(self):
        """
        The session has ended due to session expiration.
        """
        if self.expiry_time:
            return self.expiry_time <= timezone.now()
        return False
    session_expired.boolean = True
    session_expired.short_description = _("Session expired")

    def pretty_time_on_site(self):
        if self.time_on_site is not None:
            return timedelta(seconds = self.time_on_site)
    pretty_time_on_site.short_description = _("Time on site")

class PageView(models.Model):
    visit = models.ForeignKey(
        Visit,
        related_name = "pageviews",
        on_delete = models.CASCADE,
        verbose_name = _("Visit"),
    )
    url = models.TextField(_("URL"))
    referer = models.TextField(_("Referer"))
    query_string = models.TextField(_("Query string"))
    method = models.CharField(_("Method"), max_length = 10)
    view_time = models.DateTimeField(_("View time"))

    objects = PageviewManager["PageView"]()

    class Meta(object):
        verbose_name = _("page view")
        verbose_name_plural = _("page views")
        ordering = ("-view_time",)
