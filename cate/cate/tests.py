from datetime import date

from django.test import TestCase

from .templatetags.school_year import school_year


class SchoolYearTests(TestCase):
	"""
	Tests for `school_year()` filter.
	"""
	def test_after_august(self):
		"""
		01/08/2022, 01/09/2022, ..., 01/12/2022 => 2022-2023
		"""
		for month in range(8, 12 + 1):
			self.assertEqual(school_year(date(2022, month, 1)), "2022-2023")

	def test_before_august(self):
		"""
		01/01/2022, 01/02/2022, ..., 01/08/2022 => 2021-2022
		"""
		for month in range(1, 7 + 1):
			self.assertEqual(school_year(date(2022, month, 1)), "2021-2022")
