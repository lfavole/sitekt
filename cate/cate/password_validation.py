import hashlib

import requests
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from . import settings


class PwnedPasswordValidator:
    """
    This password validator returns a ValidationError if the PWNED Passwords API
    detects the password in its data set. Note that the API is heavily rate-limited,
    so there is a timeout (PWNED_VALIDATOR_TIMEOUT).

    If self.fail_safe is True, anything besides an API-identified bad password
    will pass, including a timeout. If self.fail_safe is False, anything
    besides a good password will fail and raise a ValidationError.
    """

    def __init__(self, timeout=5, fail_safe=False, min_breaches=1):
        self.timeout = timeout
        self.fail_safe = fail_safe
        self.min_breaches = min_breaches

    def validate(self, password, _user=None):
        if not self.check_valid(password):
            raise ValidationError(_("Your password was determined to have been involved in a major security breach."))

    def check_valid(self, password):
        """
        Tests that a password is valid using the API. Uses k-anonymity model in v2 API.

        If self.fail_safe is True, anything besides a bad password will
        return True. If self.fail_safe is False, anything besides a good password
        will return False.

        :param password: The password to test
        :return: True if the password is valid. Else, False.
        """

        if settings.custom_settings.OFFLINE:
            return True

        error_fail_msg = _(
            "We could not validate the safety of this password. "
            "This does not mean the password is invalid. Please try again later."
        )

        try:
            p_hash = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
            response = requests.get(f"https://api.pwnedpasswords.com/range/{p_hash[0:5]}", timeout=self.timeout)

            if self.get_breach_count(p_hash, response.text) >= self.min_breaches:
                return False
            if self.fail_safe:
                return True
            if response.status_code in [400, 429, 500]:
                raise ValidationError(error_fail_msg)
            if response.status_code == 200:
                return True
        except (requests.exceptions.RequestException, IndexError, ValueError) as exc:
            if not self.fail_safe:
                raise ValidationError(error_fail_msg) from exc
            return True

        if self.fail_safe:
            return True
        raise ValidationError(error_fail_msg)

    def get_help_text(self):
        return _("Your password must not have been detected in a major security breach.")

    @staticmethod
    def get_breach_count(p_hash: str, response_text: str):
        for line in response_text.splitlines():
            hash, count = line.split(":")
            if p_hash[5:] == hash:
                return int(count)
        return 0
