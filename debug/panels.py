import html
import sys
from urllib.parse import urlencode

from debug.client import GitClient, GitHubClient
from debug_toolbar.decorators import render_with_toolbar_language, require_show_toolbar
from debug_toolbar.panels import Panel
from debug_toolbar.toolbar import DebugToolbar
from django.core.handlers import exception
from django.core.handlers.exception import response_for_exception
from django.http import Http404, HttpRequest, HttpResponse
from django.template.loader import render_to_string
from django.urls import path
from django.utils.safestring import SafeString
from django.utils.translation import gettext_lazy as _
from django.views.debug import ExceptionReporter, technical_404_response
from django.views.decorators.clickjacking import xframe_options_exempt


class ErrorPanel(Panel):
    """
    A panel that displays debug information about 404 or 500 errors.
    """

    title = _("Error")  # type: ignore
    template = "debug_toolbar/panels/error.html"  # type: ignore

    @property
    def nav_subtitle(self):
        exc_info = self.get_stats().get("exc_info")
        if exc_info is None:
            return _("No error")
        return f"{exc_info[0].__name__}: {exc_info[1]}"

    @property
    def has_content(self):
        return self.get_stats().get("exc_info") is not None

    def generate_stats(self, request, response):
        self.toolbar.store()  # ensure that store_id exists
        self.record_stats(
            {
                "request": request,
                "store_id": self.toolbar.store_id,
            }
        )

    def enable_instrumentation(self):
        exception._old_response_for_exception = response_for_exception  # type: ignore

        def new_response_for_exception(request: HttpRequest, exc: Exception):
            """
            Saves the exception and continues normal processing.
            """
            self.record_stats({"exc_info": sys.exc_info()})
            return exception._old_response_for_exception(request, exc)  # type: ignore

        exception.response_for_exception = new_response_for_exception

    def disable_instrumentation(self):
        exception.response_for_exception = exception._old_response_for_exception  # type: ignore

    @property
    def error_content(self):
        """
        Returns the content of the `<iframe>` that contains the error.
        """
        stats = self.get_stats()
        exc_info = stats.get("exc_info")
        request = stats.get("request")

        if exc_info is None:
            return ""

        if isinstance(stats["exc_info"][1], Http404):
            return technical_404_response(request, exc_info[1])

        reporter = ExceptionReporter(request, *exc_info)
        return reporter.get_traceback_html()

    @classmethod
    def get_urls(cls):
        return [path("error-panel", error_panel_view, name="error_panel")]


@require_show_toolbar
@render_with_toolbar_language
@xframe_options_exempt
def error_panel_view(request):
    """
    Render the contents of the error.
    """
    toolbar = DebugToolbar.fetch(request.GET["store_id"])
    if toolbar is None:
        return HttpResponse()

    panel = toolbar.get_panel_by_id("ErrorPanel")
    return HttpResponse(panel.error_content)


class GitInfoPanel(Panel):
    # pylint: disable=C0116
    title = _("Revision")  # type: ignore
    template = "debug_toolbar/panels/git_info.html"  # type: ignore
    _client = None
    _github_client = None

    @property
    def client(self):
        if self._client is None:
            self._client = GitClient()
        return self._client

    @property
    def github_client(self):
        if self._github_client is None:
            self._github_client = GitHubClient()
        return self._github_client

    @property
    def nav_subtitle(self):
        if self.client.is_repository:
            return self.client.short_hash
        return _("No repository was detected.")

    @property
    def has_content(self):
        return self.client.is_repository

    @property
    def content(self):
        labels = {
            "short_hash": _("Short hash"),
            "hash": _("Hash"),
            "author_info": _("Author"),
            "committer_info": _("Committer"),
            "date": _("Updated at"),
            "subject": _("Subject"),
            "body": _("Body"),
            "branch_name": _("Branch name"),
            "gpg_signature": _("Signature status"),
            "author_profile": _("Author profile"),
            "committer_profile": _("Committer profile"),
            "url": _("URL"),
        }

        parts: dict[str, list[tuple[str, str]]] = {}
        for client, title in [
            (self.client, _("Git information")),
            (self.github_client, _("GitHub information")),
        ]:
            parts[title] = []

            client_class = type(client)
            for attr in client_class.__dict__.keys():  # we use __dict__ because we need the order
                if attr not in labels:
                    continue
                if not isinstance(getattr(client_class, attr), property):
                    continue

                value = getattr(client, attr)
                if isinstance(value, dict):
                    value = SafeString(
                        "<br>".join(
                            # Translators: add a space before colon if needed
                            f"<b>{html.escape(key)}</b>" + _(":") + f" {html.escape(value)}"
                            for key, value in value.items()
                        )
                    )
                if attr == "url":
                    value = SafeString(f'<a href="{html.escape(value)}" target="_blank">{html.escape(value)}</a>')
                if value is None or value == "":
                    value = "-"
                parts[title].append((labels[attr], value))

        return render_to_string(self.template, {"parts": parts})
