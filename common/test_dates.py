import datetime
from zoneinfo import ZoneInfo

from common.test_utils import REMOVED, DefaultArgs, TestCase, clean
from django.conf import settings
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.formats import time_format
from django.utils.timezone import get_default_timezone, now as get_now

from cate.templatetags.format_date import format_date

from .models import Date

now = datetime.datetime(2023, 1, 1, 12, 0, 0)
one_day = datetime.timedelta(days=1)
one_hour = datetime.timedelta(hours=1)

def_args = DefaultArgs(
    {
        "name": "Test date",
        "place": "Test place",
        "start_date": now.date(),
        "end_date": now.date() + one_day,
        "start_time": now.time(),
        "end_time": (now + one_hour).time(),
        "time_text": "",
        "cancelled": False,
    }
)


class DateModelTests(TestCase):
    """
    Tests on the `Date` model.
    """

    def test_normal(self):
        """
        Normal date
        """
        date = Date(**def_args())
        with self.assertValidationOK():
            clean(date)

    def test_invalid_date(self):
        """
        start_date > end_date
        """
        date = Date(**def_args(start_date=now, end_date=now - one_day))
        with self.assertRaises(ValidationError):
            clean(date)

    def test_only_end_date(self):
        """
        start_date = ?
        end_date = ...
        """
        date = Date(**def_args(start_date=REMOVED, end_date=now))
        with self.assertRaises(ValidationError):
            clean(date)

    def test_invalid_time(self):
        """
        start_time > end_time
        """
        date = Date(**def_args(start_date=now.date(), start_time=now.time(), end_date=now.date(), end_time=(now - one_hour).time()))
        with self.assertRaises(ValidationError):
            clean(date)

    def test_same_start_and_end_time(self):
        """
        start_time = end_time = ...
        end_date and end_time removed
        """
        date = Date(**def_args(end_date=now.date(), end_time=now.time()))
        with self.assertValidationOK():
            clean(date)
        self.assertIsNone(date.end_date)
        self.assertIsNone(date.end_time)

    def test_no_time(self):
        """
        start_time = ?
        end_time = ?
        time_text = ?
        """
        date = Date(**def_args(start_time=REMOVED, end_time=REMOVED, time_text=REMOVED))
        with self.assertValidationOK():
            clean(date)

    def test_only_start_time(self):
        """
        start_time = ...
        end_time = ?
        """
        date = Date(**def_args(end_time=REMOVED))
        with self.assertRaises(ValidationError):
            clean(date)

    def test_only_end_time(self):
        """
        start_time = ?
        end_time = ...
        """
        date = Date(**def_args(start_time=REMOVED))
        with self.assertRaises(ValidationError):
            clean(date)

    def test_all_time_fields(self):
        """
        start_time = ...
        end_time = ...
        time_text = ...
        """
        date = Date(**def_args(time_text="..."))
        with self.assertRaises(ValidationError):
            clean(date)

    def test_start_end_date(self):
        """
        start_date = x
        => start = x (date)
        => end = x + 1 day (date)
        """
        for date_to_try in [
            now,  # January 1st
            now + datetime.timedelta(days=30),  # January 31st (month overflow)
            now - datetime.timedelta(days=1),  # December 31st (year overflow)
        ]:
            date = Date(start_date=date_to_try.date())
            start = date_to_try.date()
            end = start + datetime.timedelta(days=1)
            self.assertEqual(date.start, start)
            self.assertEqual(date.end, end)

    def test_start_end_datetime(self):
        """
        start_date = x
        start_time = y
        => start = x at y (datetime)
        => end = x at y + 1 hour (datetime)
        """
        for date_to_try in [
            now,  # January 1st at 12:00
            now - datetime.timedelta(days=1),  # December 31st at 12:00
            now + datetime.timedelta(days=30),  # January 31st at 12:00
            now + datetime.timedelta(hours=23, minutes=30),  # January 1st at 23:30 (day overflow)
            now.replace(hour=0, minute=0),  # January 1st at 00:00
        ]:
            date_to_try = date_to_try.replace(tzinfo=ZoneInfo(settings.TIME_ZONE))
            date = Date(start_date=date_to_try.date(), start_time=date_to_try.time())
            start = date_to_try
            end = start + datetime.timedelta(hours=1)
            self.assertEqual(date.start, start)
            self.assertEqual(date.end, end)

    def test_past(self):
        """
        start = now - 1 day => past
        start = now - 1 hour - 5 seconds* => past

        start = now - 5 seconds* => current
        start = now - 50 minutes => current

        start = now + 5 seconds* => future

        Also checks that the 2 other attributes are false.

        * avoids race conditions
        """
        # timezone info is lost when instantiating the Date object
        now = get_now().astimezone(get_default_timezone())
        past_checks = [
            now - datetime.timedelta(days=1),
            now - datetime.timedelta(hours=1, seconds=5),
        ]
        current_checks = [
            now - datetime.timedelta(seconds=5),
            now - datetime.timedelta(minutes=50),
        ]
        future_checks = [
            now + datetime.timedelta(seconds=5),
            now + datetime.timedelta(days=1),
        ]

        for date_to_try in past_checks:
            date = Date(start_date=date_to_try.date(), start_time=date_to_try.time())
            self.assertTrue(date.is_past, f"The date {date_to_try} should be past")

            self.assertFalse(date.is_current, f"The date {date_to_try} should not be current")
            self.assertFalse(date.is_future, f"The date {date_to_try} should not be future")

        for date_to_try in current_checks:
            date = Date(start_date=date_to_try.date(), start_time=date_to_try.time())
            self.assertTrue(date.is_current, f"The date {date_to_try} should be current")

            self.assertFalse(date.is_past, f"The date {date_to_try} should not be past")
            self.assertFalse(date.is_future, f"The date {date_to_try} should not be future")

        for date_to_try in future_checks:
            date = Date(start_date=date_to_try.date(), start_time=date_to_try.time())
            self.assertTrue(date.is_future, f"The date {date_to_try} should be future")

            self.assertFalse(date.is_past, f"The date {date_to_try} should not be past")
            self.assertFalse(date.is_current, f"The date {date_to_try} should not be current")


class DateTests(TestCase):
    """
    Tests on the dates page.
    """

    def test_no_dates(self):
        """
        No dates => "Aucune date" in the page
        """
        response = self.client.get(reverse("dates"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Aucune date")
        self.assertQuerySetEqual(response.context["dates"], [])

    def test_one_date(self):
        """
        A date is shown in the page
        """
        date = Date.objects.create(**def_args())

        response = self.client.get(reverse("dates"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, format_date(date.start_date, date.end_date))
        self.assertContains(response, time_format(date.start_time, "G:i"))  # type: ignore
        self.assertContains(response, "– " + time_format(date.end_time, "G:i"))  # type: ignore
        self.assertQuerySetEqual(response.context["dates"], [date])
