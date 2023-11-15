import datetime
import json
from pathlib import Path
from typing import Literal

from dateutil.easter import easter
from django.http import HttpRequest
from fpdf.enums import Align, XPos, YPos

from cate.abbreviation import abbreviation

from ..models import Year
from . import PDF

HERE = Path(__file__).resolve()
DATA = HERE.parent.parent.parent.parent / "data"

fr_months = [
    "",
    "janvier",
    "février",
    "mars",
    "avril",
    "mai",
    "juin",
    "juillet",
    "août",
    "septembre",
    "octobre",
    "novembre",
    "décembre",
]
fr_weekdays = "LMMJVSD"


class DateContainer(
    list[tuple[Literal["event", "date", "holidays", "ferie"], str, datetime.date, datetime.date | None, bool]]
):
    easter_date: datetime.date

    def add_date(self, name: str, start_date: datetime.date, end_date: datetime.date | None = None, display=True):
        self.append(("date", name, start_date, end_date, display))

    def add_event(self, name: str, date: datetime.date, display=True):
        self.append(("event", name, date, None, display))

    def add_holidays(self, name: str, start: datetime.date, end: datetime.date):
        if "Ascension" in name and (end - start) == datetime.timedelta(days=1):
            # start = Friday, end = Saturday
            start -= datetime.timedelta(days=2)  # Wednesday
            end += datetime.timedelta(days=2)  # Monday
        self.append(("holidays", name, start, end, True))

    def add_ferie(self, name: str, date: datetime.date, display=True):
        self.append(("ferie", name, date, None, display))

    def add_easter_date(self, name: str, days_number: int, display=True):
        date = self.easter_date + datetime.timedelta(days=days_number)
        self.append(("date", name, date, None, display))

    def add_easter_ferie(self, name: str, days_number: int, display=True):
        date = self.easter_date + datetime.timedelta(days=days_number)
        self.append(("ferie", name, date, None, display))

    def __contains__(self, value):
        return self.contains(value)

    def contains(self, value, include_hidden=True):
        for date in self:
            if self.date_contains(date, value, include_hidden):
                return True

        return False

    @staticmethod
    def date_contains(date, value, include_hidden=True):
        if not date[4] and not include_hidden:
            return False

        if date[3]:
            if date[2] <= value < date[3]:
                return True
        else:
            if value == date[2]:
                return True

        return False

    def filter(self, *date_types: Literal["event", "date", "holidays", "ferie"]):
        new = type(self)()
        for date in self:
            if any(date[0] == date_type for date_type in date_types):
                new.append(date)
        return new

    def is_a(self, value: datetime.date, *date_types: Literal["event", "date", "holidays", "ferie"]):
        return value in self.filter(*date_types)

    def get_dates_for(self, value: datetime.date) -> "zip[tuple[str, ...]]":
        ret = [date[1] for date in self if self.date_contains(date, value, False) and date[0] != "holidays"]
        return zip(*(abbreviation(date) for date in ret))


def get_epiphanie(year: int):
    for day in range(2, 8 + 1):
        date = datetime.date(year, 1, day)
        if date.weekday() == 6:
            return date

    raise ValueError(f"No Sunday between January 2-8 {year}")


class Calendar(PDF):
    filename = "calendrier"

    def __init__(self, *args, **kwargs):
        super().__init__("L", *args, **kwargs)

    def render(self, app: Literal["espacecate", "aumonerie"], request: HttpRequest):
        start_year = Year.get_current().start_year

        self.set_auto_page_break(False, margin=10)

        title = {
            "espacecate": "Calendrier KT et EVF",
            "aumonerie": "Calendrier aumônerie",
        }.get(app, "Calendrier")
        title_height = 10
        month_height = 8
        day_height = (self.eph - title_height - month_height) / 31
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

        special_dates.add_ferie("Assomption", datetime.date(start_year, 8, 15), False)
        special_dates.add_ferie("Toussaint", datetime.date(start_year, 11, 1))
        special_dates.add_ferie("Armistice", datetime.date(start_year, 11, 11), False)
        special_dates.add_ferie("Noël", datetime.date(start_year, 12, 25))
        special_dates.add_ferie("Jour de l'An", datetime.date(start_year + 1, 1, 1), False)
        special_dates.add_date("Épiphanie", get_epiphanie(start_year + 1))
        special_dates.add_ferie("Fête du Travail", datetime.date(start_year + 1, 5, 1), False)
        special_dates.add_ferie("Armistice", datetime.date(start_year + 1, 5, 8), False)

        special_dates.add_easter_date("Merc. Cendres", -46)
        special_dates.add_easter_date("Rameaux", -7)
        special_dates.add_easter_date("Jeudi Saint", -3)
        special_dates.add_easter_date("Pâques", 0)
        special_dates.add_easter_ferie("Lundi de Pâques", 1, False)
        special_dates.add_easter_ferie("Ascension", 39)
        special_dates.add_easter_date("Pentecôte", 49)
        special_dates.add_easter_ferie("Lundi de Pentecôte", 50, False)

        if app == "espacecate":
            from espacecate.models import Date
        elif app == "aumonerie":
            from aumonerie.models import Date

        for date in Date.objects.all():
            special_dates.add_date(
                date.short_name or date.name,
                date.start_date,
                date.end_date + datetime.timedelta(days=1) if date.end_date else date.end_date,
            )

        self.title = f"{title} {start_year}-{start_year + 1}"

        _DAYS_IN_MONTH = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        def get_days_in_month(year: int, month: int):
            if month == 2 and year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
                return 29
            return _DAYS_IN_MONTH[month]

        months_list = [range(8, 12 + 1), range(1, 6 + 1)]
        for count, months in enumerate(months_list):
            year = start_year + count

            self.set_left_margin(10)
            self.add_page()
            self.set_font("Montserrat", "B", 22)
            self.cell(
                0,
                title_height,
                f"{title} : {fr_months[months[0]].capitalize()} – {fr_months[months[-1]].capitalize()} {start_year + count}",
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
                align=Align.C,
            )

            month_width = self.epw / len(months)

            for month_n, month in enumerate(months):
                # pdf.set_left_margin(10 + month_width * month_n)
                self.y = 10 + title_height
                days_number = get_days_in_month(year, month)

                self.set_font("Montserrat", "B", 16)
                self.set_fill_color(255, 120, 120)
                self.set_text_color(255)
                self.cell(
                    month_width,
                    month_height,
                    fr_months[month].capitalize(),
                    border=True,
                    fill=True,
                    new_x=XPos.LMARGIN,
                    new_y=YPos.NEXT,
                    align=Align.C,
                )

                self.set_font("Montserrat", "", 12)
                self.set_text_color(0)
                for day in range(1, days_number + 1):
                    datetime_day = datetime.date(year, month, day)
                    sunday = datetime_day.weekday() == 6
                    ferie = special_dates.is_a(datetime_day, "ferie")
                    holidays = special_dates.is_a(datetime_day, "holidays")

                    fill = False
                    if ferie:
                        self.set_fill_color(255, 255, 120)
                        fill = True
                    elif sunday:
                        self.set_fill_color(200, 200, 255)
                        fill = True
                    self.cell(
                        day_width,
                        day_height,
                        str(day),
                        border=True,
                        align=Align.C,
                        fill=fill,
                    )
                    self.cell(
                        weekday_width,
                        day_height,
                        fr_weekdays[datetime_day.weekday()],
                        border=True,
                        align=Align.C,
                        fill=fill,
                    )

                    fill = False
                    if holidays:
                        self.set_fill_color(170, 255, 170)
                        fill = True
                    elif sunday:
                        self.set_fill_color(200, 200, 255)
                        fill = True

                    text = ""
                    width = month_width - day_width - weekday_width
                    stretching = 100
                    for dates in special_dates.get_dates_for(datetime_day):
                        text = " – ".join(dates)
                        if not text:
                            break  # avoid setting the font size if there is no text

                        self.set_font_size(10)
                        text_width = self.get_string_width(text)

                        # for a given text:
                        #         100 % <--> text_width mm
                        #  stretching % <--> width mm

                        if text_width:  # avoid division by zero
                            padding = (self.font_size_pt / 3) / self.k * 2  # 4 pt on each side
                            stretching = (width - padding) * 100 / text_width
                        else:
                            stretching = 100

                        if stretching >= 75:
                            break

                    if stretching < 100:
                        self.set_stretching(stretching)

                    self.cell(
                        width,
                        day_height,
                        text,
                        border=True,
                        align=Align.C,
                        fill=fill,
                        new_x=XPos.LMARGIN,
                        new_y=YPos.NEXT,
                    )

                    if stretching != 100:
                        self.set_stretching(100)

                    self.set_font_size(12)

                self.l_margin += month_width
                self.x = self.l_margin
