from urllib.parse import urlencode

from allauth.account.utils import get_next_redirect_url
from django import template
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.template.defaultfilters import stringfilter
from django.utils.http import url_has_allowed_host_and_scheme

register = template.Library()


@register.simple_tag(takes_context=True)
def redirect_field(context):
    """
    Return "?next=..." if it was provided.
    """
    redirect_to = get_next_redirect_url(context.request, REDIRECT_FIELD_NAME)
    if not redirect_to:
        return ""
    return "?" + urlencode({REDIRECT_FIELD_NAME: redirect_to})
