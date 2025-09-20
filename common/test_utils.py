from contextlib import contextmanager

from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase as DjangoTestCase


class DefaultArgs(dict):
    """
    Dict that can be edited when called.
    Example :
    >>> DefaultArgs({"a": "b", "c": "d", "e": "f"})(a = REMOVED, c = "e")
    {"c": "e", "e": "f"}
    """

    REMOVED = object()

    def _fix_post(self, value):
        if value is None:
            return ""
        return str(value)

    def __call__(self, *, post=False, **names):
        args = type(self)(self)  # copy

        for name, value in names.items():
            if value == self.REMOVED:
                args.pop(name)
            else:
                args[name] = value

        if post:
            for key, value in args.items():
                args[key] = self._fix_post(value)

        return args


REMOVED = DefaultArgs.REMOVED


def clean(model: models.Model, exclude=None):
    """
    Clean a model. Same as `model.full_clean()` but the execution is stopped when a `ValidationError` is raised.
    """
    model.clean_fields(exclude)
    model.clean()
    model.validate_unique(exclude)
    model.validate_constraints(exclude)  # type: ignore


class TestCase(DjangoTestCase):
    """
    Test case class with custom methods.
    """

    # https://gist.github.com/hzlmn/6b7bc384301afefcac6de3829bd4c032
    @contextmanager
    def assertValidationOK(self):
        """
        Fails if the content of the with statement raises a ValidationError.
        """
        try:
            yield
        except ValidationError:
            self.fail("ValidationError raised")
