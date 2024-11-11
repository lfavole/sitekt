from django.conf import settings
from django.core.cache import cache

from .cache import instance_cache_key

SESSION_COOKIE_AGE = getattr(settings, "SESSION_COOKIE_AGE")


def post_save_cache(sender, instance, **_kwargs):
    cache.set(instance_cache_key(instance), instance, SESSION_COOKIE_AGE)
