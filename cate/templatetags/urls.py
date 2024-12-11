from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def url_for_app(context, value):
    """
    Returns an URL for the current app.
    """
    app = context.request.resolver_match.url_name.split("_")[0]
    return reverse(f"{app}_{value}")
