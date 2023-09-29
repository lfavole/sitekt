import datetime as dt
import html
import subprocess as sp
from time import time
from typing import Any

import custom_settings
import requests
from django.utils.safestring import SafeString
from django.utils.translation import gettext_lazy as _


def returns_on_fail(return_value):
    def decorator(func):
        def inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except sp.CalledProcessError:
                return return_value

        return inner

    return decorator


def format_name_email(name: str, email: str):
    name = name.strip()
    email = email.strip()
    if name == email or not name:
        return email
    return f"{name} <{email}>"


class GitClient:
    @property
    @returns_on_fail(False)
    def is_repository(self):
        return self._execute_git("rev-parse", "--is-inside-work-tree").startswith("true")

    @property
    @returns_on_fail(None)
    def hash(self):
        return self._execute_git_show("%H")

    @property
    @returns_on_fail(None)
    def short_hash(self):
        return self._execute_git_show("%h")

    @property
    @returns_on_fail(None)
    def branch_name(self):
        return self._execute_git("rev-parse", "--abbrev-ref", "HEAD")

    @property
    @returns_on_fail(None)
    def author_info(self):
        return format_name_email(*self._execute_git_show("%an%x00%ae").split("\0"))

    @property
    @returns_on_fail(None)
    def committer_info(self):
        return format_name_email(*self._execute_git_show("%cn%x00%ce").split("\0"))

    @property
    @returns_on_fail(None)
    def date(self):
        iso_format = self._execute_git_show("%ci")
        try:
            return dt.datetime.fromisoformat(iso_format)
        except ValueError:
            return None

    @property
    @returns_on_fail(None)
    def subject(self):
        return self._execute_git_show("%s")

    @property
    @returns_on_fail(None)
    def body(self):
        return self._execute_git_show("%b")

    @property
    @returns_on_fail(None)
    def gpg_signature(self):
        command = "%x00".join(["%G?", "%GK", "%GF", "%GT"])
        status, key, fingerprint, trust_level = self._execute_git_show(command).split("\0")
        status = {
            "G": _("Valid signature"),
            "B": _("Invalid signature"),
            "U": _("Unknown validity"),
            "X": _("Expired signature"),
            "Y": _("Expired key"),
            "R": _("Revoked key"),
            "E": _("Can't check for validity"),
            "N": _("No signature"),
        }.get(status, status)
        return {
            _("Status"): status,
            _("Key"): key,
            _("Key fingerprint"): fingerprint,
            _("Trust level"): trust_level,
        }

    def _execute_git_show(self, format_text, commit="HEAD"):
        return self._execute_git("show", "--quiet", f"--format={format_text}", commit).strip()

    _outputs = {}

    def _execute_git(self, *args):
        if args in self._outputs:
            data = self._outputs[args]
            if time() - data[0] < 60:  # cache for one minute
                if isinstance(data[1], Exception):
                    raise data[1]
                return data[1]

        ts = time()
        try:
            output = sp.check_output(["git", *args], encoding="utf-8")
        except sp.CalledProcessError as err:
            self._outputs[args] = (ts, err)
            raise

        self._outputs[args] = (ts, output)
        return output


class GitHubClient:
    # cf. https://docs.github.com/en/rest/commits/commits#get-a-commit
    _data = (0, None)

    @property
    def api_data(self) -> dict[str, Any]:
        if custom_settings.OFFLINE:
            return {}

        if time() - self._data[0] < 60 and self._data[1]:
            return self._data[1]

        parts = custom_settings.GITHUB_REPO.rstrip("/").split("/")
        req = requests.get(f"https://api.github.com/repos/{parts[-2]}/{parts[-1]}/commits/HEAD")
        ts = time()
        data = req.json()
        self._data = (ts, data)
        return data

    @property
    def hash(self):
        return self.api_data.get("sha", "")

    @property
    def short_hash(self):
        return self.hash[0:7]

    def info(self, who: str):
        data = self.api_data.get("commit", {}).get(who, {})
        return format_name_email(data.get("name", ""), data.get("email", ""))

    def profile(self, who: str):
        data = self.api_data.get(who, {})
        url = data.get("html_url", "")
        picture_url = data.get("avatar_url", "")
        ret = html.escape(data.get("login", ""))
        if picture_url:
            ret += f'<img src="{html.escape(picture_url)}">'
        if url:
            ret = f'<a href="{html.escape(url)}" target="_blank">{ret}</a>'
        return SafeString(ret)

    @property
    def author_info(self):
        return self.info("author")

    @property
    def author_profile(self):
        return self.profile("author")

    @property
    def committer_info(self):
        return self.info("committer")

    @property
    def committer_profile(self):
        return self.profile("committer")

    @property
    def date(self):
        iso_format = self.api_data.get("commit", {}).get("committer", {}).get("date", "")
        try:
            return dt.datetime.fromisoformat(iso_format)
        except ValueError:
            return None

    @property
    def subject(self):
        return self.api_data.get("commit", {}).get("message", "")

    @property
    def gpg_signature(self):
        data = self.api_data.get("commit", {}).get("verification", {})
        verified = data.get("verified")
        status = data.get("status", "")
        status = {
            "expired_key": _("Expired key"),
            "not_signing_key": _("The key is not a signing key"),
            "gpgverify_error": _("Error while checking for validity"),
            "gpgverify_unavailable": _("Can't check for validity"),
            "unsigned": _("No signature"),
            "unknown_signature_type": _("Unknown signature type"),
            "no_user": _("No user associated"),
            "unverified_email": _("Unverified email address"),
            "bad_email": _("Bad email address"),
            "unknown_key": _("Unknown key"),
            "malformed_signature": _("Malformed signature"),
            "invalid": _("Invalid signature"),
            "valid": _("Valid signature"),
        }.get(status, status)
        verified = {True: _("yes"), False: _("no")}.get(verified, _("unknown"))  # type: ignore
        return {
            _("Verified"): verified,
            _("Status"): status,
        }

    @property
    def url(self):
        return self.api_data.get("html_url", "")
