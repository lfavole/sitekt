from django.test import TestCase

from .models import Year

y1 = 2022
y2 = 2023
y3 = 2024


class YearTests(TestCase):
    """
    Tests on the `Year` model (automatic active year changing).
    """

    def test_one_year(self):
        """
        * 2022 => inactive

        => 2022 becomes active
        """
        year1 = Year(year=y1)
        year1.save()

        self.assertTrue(year1.is_active, "The year is not active")

    def test_two_years(self):
        """
        * 2022 => active
        * 2023 => active

        => 2022 becomes inactive but 2023 stays active
        """
        year1 = Year(year=y1, is_active=True)
        year1.save()

        year2 = Year(year=y2, is_active=True)
        year2.save()

        self.assertTrue(not year1.is_active, "The first year is active")
        self.assertTrue(year2.is_active, "The second year is not active")

    def test_two_years_deleted(self):
        """
        * 2022 => active
        * 2023 => inactive
        * delete 2022

        => 2023 becomes active
        """
        year1 = Year(year=y1, is_active=True)
        year1.save()

        year2 = Year(year=y2)
        year2.save()

        year1.delete()

        self.assertTrue(year2.is_active, "The second year is not active")
