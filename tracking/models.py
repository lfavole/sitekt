from datetime import timedelta
from typing import Any

import requests
import user_agents
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

from .managers import PageviewManager, VisitManager


class Visit(models.Model):
    session_key = models.CharField(_("session key"), max_length=40)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="visit_history",
        null=True,
        editable=False,
        on_delete=models.SET_NULL,
        verbose_name=_("User"),
    )
    ip_address = models.GenericIPAddressField(_("IP address"))
    user_agent = models.TextField(_("user agent"))
    start_time = models.DateTimeField(_("start time"), default=timezone.now)
    expiry_time = models.DateTimeField(_("session expiry time"))
    time_on_site = models.IntegerField(_("time on site"))

    objects = VisitManager["Visit"]()

    class Meta(object):
        verbose_name = _("visit")
        ordering = ("-start_time",)
        permissions = (("visitor_log", "Can view visitor"),)

    def ip_address_location(self):
        req = requests.get(
            f"http://ip-api.com/json/{self.ip_address}",
            {
                "fields": "status,message,city,regionName,country,mobile,proxy,hosting",
                "lang": "fr",
            },
        )
        try:
            data: dict[str, Any] = req.json()
        except requests.JSONDecodeError as err:
            return f"JSONDecodeError : {err}"
        if data.get("status") == "fail":
            return data.get("message", "")
        extra = []
        if data.get("mobile"):
            extra.append(_("mobile connection"))
        if data.get("proxy"):
            extra.append(_("proxy"))
        if data.get("hosting"):
            extra.append(_("hosting"))

        # Translators: This string is used as a separator between list elements
        sep = gettext(", ")
        ret = sep.join(
            (
                data.get("city", ""),
                data.get("regionName", ""),
                data.get("country", ""),
            )
        )
        if extra:
            ret += " (" + sep.join(extra) + ")"
        return ret

    ip_address_location.short_description = _("IP address location")

    def pretty_user_agent(self):
        return str(user_agents.parse(self.user_agent))

    pretty_user_agent.short_description = _("Information about user agent")

    def session_expired(self):
        """
        The session has ended due to session expiration.
        """
        if self.expiry_time:
            return self.expiry_time <= timezone.now()
        return False

    session_expired.boolean = True
    session_expired.short_description = _("session expired")

    def pretty_time_on_site(self):
        if self.time_on_site is not None:
            return timedelta(seconds=self.time_on_site)

    pretty_time_on_site.short_description = _("time on site")


class PageView(models.Model):
    visit = models.ForeignKey(
        Visit,
        related_name="pageviews",
        on_delete=models.CASCADE,
        verbose_name=_("Visit"),
    )
    url = models.TextField(_("URL"))
    referer = models.TextField(_("referer"))
    query_string = models.TextField(_("query string"))
    method = models.CharField(_("method"), max_length=10)
    view_time = models.DateTimeField(_("view time"))

    objects = PageviewManager["PageView"]()

    class Meta(object):
        verbose_name = _("page view")
        verbose_name_plural = _("page views")
        ordering = ("-view_time",)
