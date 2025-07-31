from html import escape
import html
import re

from allauth.account import views
from allauth.account import adapter
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter, get_adapter
from allauth.socialaccount.models import SocialApp
from django.conf import settings
from django.contrib.messages import info
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import resolve_url
from django.template.loader import render_to_string as real_render_to_string
from django.urls import Resolver404, resolve
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from common.models import Year


class Adapter(DefaultAccountAdapter):
    """Dummy adapter."""

    def render_mail(self, template_prefix, email, context):
        context["subject"] = render_to_string(f"{template_prefix}_subject.txt", context)
        context["request"] = self.request
        return super().render_mail(template_prefix, email, context)


def patch(old):
    """Add parameters for One Tap sign-in and the registering form."""
    def get_context_data(self, **kwargs):
        ret = old(self, **kwargs)

        # pass settings to the template for One Tap sign-in
        try:
            adapter: DefaultSocialAccountAdapter = get_adapter()
            app: SocialApp = adapter.get_app(self.request, "google")
            ret["GOOGLE_CLIENT_ID"] = app.client_id
        except SocialApp.DoesNotExist:
            pass

        ret["GOOGLE_REDIRECT_URI"] = self.request.build_absolute_uri(resolve_url("google_callback"))

        try:
            resolver_match = resolve(ret["redirect_field_value"])
        except Resolver404:
            pass
        else:
            if resolver_match.route.split("_")[0] == "inscription":
                info(
                    self.request,
                    mark_safe(
                        escape(
                            _("Starting this year, you will need to create an account to register your child.")
                            if Year.get_current().start_year <= 2025
                            else _("You need to create an account to register your child.")
                        )
                        + "<br>"
                        + escape(_("This will help us to simplify the registering process."))
                    ),
                )

        return ret

    return get_context_data


views.LoginView.get_context_data = patch(views.LoginView.get_context_data)
views.SignupView.get_context_data = patch(views.SignupView.get_context_data)


def markdown(data, site_url=None):
    def link(url):
        real_url = f"https://{url}" if not url.startswith("http") else url
        return f'<a href="{html.escape(real_url)}">{html.escape(url)}</a>'

    data = html.escape(data.strip())
    data = re.sub(
        r"(?:(?:https?://|www\.)[\w@:%.\+~#=-]+"
        + ("|" + re.escape(site_url) if site_url else "")
        + r")[\w()@:%\+.~#?&/=-]*(?<!\.)",
        lambda match: link(match[0]),
        data,
    )
    data = "<p>" + re.sub(r"\n{2,}", "</p><p>", data) + "</p>"
    data = data.replace("\n", "<br>")
    return data


def render_to_string(template_name, context, *args, **kwargs):
    if template_name.endswith("_message.html"):
        data = real_render_to_string(template_name[:-4] + "txt", context, *args, **kwargs)
        data = markdown(data, get_current_site(context["request"]).domain if "request" in context else None)
        return real_render_to_string(
            "account/email/base_message.html",
            {
                **context,
                "data": data,
                "SITE_NAME": settings.SITE_NAME,
            },
        )

    return real_render_to_string(template_name, context, *args, **kwargs)


adapter.render_to_string = render_to_string
