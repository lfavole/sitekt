import json
import re
from html import escape
from string import Template
from urllib.parse import quote
from urllib.request import Request, urlopen
from wsgiref.util import is_hop_by_hop

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    User model for model swapping.
    It's here if we might need to change the user model and don't unapply the migrations.
    """

    class Meta:
        verbose_name = _("user")
        permissions = [
            ("can_see_debug_toolbar", "Can see debug toolbar"),
        ]


class CustomTemplate(Template):
    idpattern = r"\w(?:\.?\w)*(?::\w+)*"
    flags = re.ASCII & re.IGNORECASE


class CustomJSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, (models.FileField, models.ImageField)):
            return o.url if o and o.name else None
        return super().default(o)


def simplify(obj):
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if obj is None:
        return None
    if isinstance(obj, (list, tuple, set)):
        return [simplify(item) for item in obj]
    if isinstance(obj, dict):
        return {simplify(key): simplify(value) for key, value in obj.items()}
    try:
        return CustomJSONEncoder().default(obj)
    except TypeError:
        return str(obj)


class Webhook(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    url = models.URLField()
    method = models.CharField(max_length=10, choices=[("GET", "GET"), ("POST", "POST"), ("PUT", "PUT"), ("DELETE", "DELETE")])
    headers = models.TextField(blank=True)
    body = models.TextField(blank=True)

    def __str__(self):
        return self.name

    def send_request(self, data):
        replace = self.make_replacer({"data": simplify(data)})
        with urlopen(
            Request(
                url=replace(self.url),
                data=replace(self.body).encode(),
                headers=self.parse_headers(replace(self.headers)),
                method=self.method,
            )
        ) as f:
            headers = {key: value for key, value in dict(f.getheaders()).items() if not is_hop_by_hop(key)}
            return HttpResponse(f.read(), status=f.getcode(), headers=headers)

    def parse_headers(self, headers):
        return {
            name: value
            for name, _, value
            in (header.partition(": ") for header in headers.splitlines())
        }

    def make_replacer(self, data):
        def replace(string):
            template = CustomTemplate(string)
            substitutions = {}

            for identifier in template.get_identifiers():
                key = identifier
                key, sep, extra_params = key.partition(":")

                value = data
                for subkey in key.split("."):
                    try:
                        subkey = int(subkey)
                    except ValueError:
                        pass
                    value = value[subkey]

                extra_params = extra_params.split(":") if extra_params else None
                for param in extra_params:
                    substitutions[identifier] = self.escape(value, param)

            return template.substitute(substitutions)

        return replace

    def escape(self, value, escape_type: str | None):
        if escape_type == "json":
            return json.dumps(value)

        if escape_type == "url":
            return quote(value)

        if escape_type == "html":
            return escape(value)

        if escape_type == "" or escape_type is None:
            return str(value)

        raise ValueError(f"Invalid escape type: {escape_type}")
