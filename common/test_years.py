from django.test import TestCase

from .models import Year

y1 = 2022
y2 = 2023


class YearTests(TestCase):
    """
    Tests on the `Year` model (automatic active year changing).
    When I mention e.g. "2022" it will mean "2022-2023"
    (I will only write the start year).
    """

    def test_current_year(self):
        """
        The current year is created
        """
        self.assertEqual(Year.objects.count(), 1, "There should be exactly one year")
        self.assertEqual(Year.objects.first().start_year, Year.get_for_date().start_year, "The start year is incorrect")

    def test_one_year(self):
        """
        * 2022 => inactive

        => 2022 becomes active
        """
        Year.objects.all().delete()  # remove the default years

        year1 = Year(start_year=y1, is_active=False)
        self.assertFalse(year1.is_active, "The year should not be active before saving")

        year1.save()

        # reload from database
        year1 = Year.objects.get(pk=year1.pk)
        self.assertTrue(year1.is_active, "The year should be active after saving")

    def test_two_years(self):
        """
        * 2022 => active
        * 2023 => active

        => 2022 becomes inactive but 2023 stays active
        """
        Year.objects.all().delete()  # remove the default years

        year1 = Year(start_year=y1, is_active=True)
        year1.save()
        self.assertTrue(year1.is_active, "The first year should be active")

        year2 = Year(start_year=y2, is_active=True)
        year2.save()

        # reload from database
        year1 = Year.objects.get(pk=year1.pk)
        year2 = Year.objects.get(pk=year2.pk)

        self.assertFalse(year1.is_active, "The first year should not be active")
        self.assertTrue(year2.is_active, "The second year should be active")

    def test_two_years_deleted(self):
        """
        * 2022 => active
        * 2023 => inactive
        * delete 2022

        => 2023 becomes active
        """
        Year.objects.all().delete()  # remove the default years

        year1 = Year(start_year=y1, is_active=True)
        year1.save()
        self.assertTrue(year1.is_active, "The first year should be active")

        year2 = Year(start_year=y2, is_active=False)
        year2.save()
        self.assertFalse(year2.is_active, "The second year should not be active")

        year1.delete()

        # reload from database
        year2 = Year.objects.get(pk=year2.pk)
        self.assertTrue(year2.is_active, "The second year should be active")
