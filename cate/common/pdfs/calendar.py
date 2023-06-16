import datetime
import json
from pathlib import Path
from typing import Literal

from dateutil.easter import easter
from fpdf import FPDF
from fpdf.enums import Align, XPos, YPos

from ..models import Year

HERE = Path(__file__).resolve()
DATA = HERE.parent.parent.parent.parent / "data"

fr_months = ["", "janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
fr_weekdays = "LMMJVSD"

class DateContainer(list[tuple[Literal["event", "date", "holidays", "ferie"], str, datetime.date, datetime.date | None]]):
	easter_date: datetime.date

	def add_date(self, name: str, start_date: datetime.date, end_date: datetime.date):
		self.append(("date", name, start_date, end_date))

	def add_event(self, name: str, date: datetime.date):
		self.append(("event", name, date, date))

	def add_holidays(self, name: str, start: datetime.date, end: datetime.date):
		self.append(("holidays", name, start, end))

	def add_ferie(self, name: str, date: datetime.date):
		self.append(("ferie", name, date, date))

	def add_easter_date(self, name: str, days_number: int):
		date = self.easter_date + datetime.timedelta(days = days_number)
		self.append(("date", name, date, date))

	def add_easter_ferie(self, name: str, days_number: int):
		date = self.easter_date + datetime.timedelta(days = days_number)
		self.append(("ferie", name, date, date))

	def __contains__(self, value):
		for date in self:
			if date[2] <= value <= (date[3] or date[2]):
				return True
		return False

	def filter(self, *date_types: Literal["event", "date", "holidays", "ferie"]):
		new = type(self)()
		for date_type in date_types:
			for date in self:
				if date[0] == date_type:
					new.append(date)
		return new

	def is_a(self, value: datetime.date, *date_types: Literal["event", "date", "holidays", "ferie"]):
		return value in self.filter(*date_types)

	def get_dates_for(self, value: datetime.date):
		ret: list[str] = []

		dates = self.filter("event", "date")
		for date in dates:
			if date[2] <= value <= (date[3] or date[2]):
				ret.append(date[1])

		return ret

def calendar_pdf(app: Literal["espacecate", "aumonerie"]):
	start_year = Year.get_current().start_year

	pdf = FPDF("L")
	pdf.add_font("Montserrat", "", str(DATA / "fonts/Montserrat-Regular.ttf"))
	pdf.add_font("Montserrat", "B", str(DATA / "fonts/Montserrat-Bold.ttf"))

	pdf.set_auto_page_break(False, margin = 10)

	title = {
		"espacecate": "Calendrier KT et EVF",
		"aumonerie": "Calendrier aumônerie",
	}.get(app, "Calendrier")
	title_height = 10
	month_height = 8
	day_height = (pdf.eph - title_height - month_height) / 31
	day_width = day_height + 1
	weekday_width = day_height

	from_iso = datetime.date.fromisoformat

	special_dates = DateContainer()
	special_dates.easter_date = easter(start_year + 1)

	with open(DATA / "fr_holidays.json") as f:
		holidays_list: list[tuple[str, str, str]] = json.load(f)
		for date in holidays_list:
			special_dates.add_holidays(
				date[0],
				from_iso(date[1]),
				from_iso(date[2]),
			)

	special_dates.add_event("Toussaint", datetime.date(start_year, 11, 1))
	special_dates.add_ferie("Noël", datetime.date(start_year, 12, 25))

	special_dates.add_easter_date("Merc. Cendres", -46)
	special_dates.add_easter_date("Rameaux", -7)
	special_dates.add_easter_date("Jeudi Saint", -3)
	special_dates.add_easter_date("Pâques", 0)
	special_dates.add_easter_ferie("Lundi de Pâques", 1)
	special_dates.add_easter_date("Ascension", 39)
	special_dates.add_easter_ferie("Ascension", 39)
	special_dates.add_easter_date("Pentecôte", 49)
	special_dates.add_easter_ferie("Lundi de Pentecôte", 50)

	if app == "espacecate":
		from espacecate.models import Date
	elif app == "aumonerie":
		from aumonerie.models import Date

	for date in Date.objects.all():
		special_dates.add_date(date.short_name or date.name, date.start_date, date.end_date)

	pdf.title = f"{title} {start_year}-{start_year + 1}"

	_DAYS_IN_MONTH = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
	def get_days_in_month(year: int, month: int):
		if month == 2 and year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
			return 29
		return _DAYS_IN_MONTH[month]

	months_list = [range(8, 12 + 1), range(1, 6 + 1)]
	for count, months in enumerate(months_list):
		year = start_year + count

		pdf.set_left_margin(10)
		pdf.add_page()
		pdf.set_font("Montserrat", "B", 22)
		pdf.cell(
			0,
			title_height,
			f"{title} : {fr_months[months[0]].title()} – {fr_months[months[-1]].title()} {start_year + count}",
			new_x = XPos.LMARGIN,
			new_y = YPos.NEXT,
			align = Align.C,
		)

		month_width = pdf.epw / len(months)

		for month_n, month in enumerate(months):
			pdf.set_left_margin(10 + month_width * month_n)
			pdf.y = 10 + title_height
			days_number = get_days_in_month(year, month)

			pdf.set_font("Montserrat", "B", 16)
			pdf.set_fill_color(255, 120, 120)
			pdf.set_text_color(255)
			pdf.cell(
				month_width,
				month_height,
				fr_months[month].title(),
				border = True,
				fill = True,
				new_x = XPos.LMARGIN,
				new_y = YPos.NEXT,
				align = Align.C,
			)

			pdf.set_font("Montserrat", "", 12)
			pdf.set_text_color(0)
			for day in range(1, days_number + 1):
				datetime_day = datetime.date(year, month, day)
				sunday = datetime_day.weekday() == 6
				ferie = special_dates.is_a(datetime_day, "ferie")
				holidays = special_dates.is_a(datetime_day, "holidays")

				fill = False
				if ferie:
					pdf.set_fill_color(255, 255, 120)
					fill = True
				elif sunday:
					pdf.set_fill_color(200, 200, 255)
					fill = True
				pdf.cell(
					day_width,
					day_height,
					str(day),
					border = True,
					align = Align.C,
					fill = fill,
				)
				pdf.cell(
					weekday_width,
					day_height,
					fr_weekdays[datetime_day.weekday()],
					border = True,
					align = Align.C,
					fill = fill,
				)

				fill = False
				if holidays:
					pdf.set_fill_color(170, 255, 170)
					fill = True
				elif sunday:
					pdf.set_fill_color(200, 200, 255)
					fill = True
				pdf.cell(
					month_width - day_width - weekday_width,
					day_height,
					" – ".join(special_dates.get_dates_for(datetime_day)),
					border = True,
					align = Align.C,
					fill = fill,
					new_x = XPos.LMARGIN,
					new_y = YPos.NEXT,
				)

	return bytes(pdf.output())
