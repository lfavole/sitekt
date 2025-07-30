import datetime
from typing import Literal

from common.models import Date, DateCategory, Year
from django.http import HttpRequest
from django.template.defaultfilters import capfirst, date
from django.utils.translation import gettext_lazy as _
from fpdf.enums import Align, XPos, YPos
from fpdf.fonts import FontFace

from cate.templatetags.format_date import format_date

from . import PDF, Table


class DatesList(PDF):
    filename = "liste_dates"

    def render(self, app: Literal["espacecate", "aumonerie"], request: HttpRequest):
        from ..views import Occurrence

        categories = DateCategory.objects.all()
        categories_query = [category for category in request.GET.get("categories", "").split(",") if category]
        if categories_query:
            categories = categories.filter(slug__in=categories_query)
        title = (
            f"Toutes les dates importantes {Year.get_current().formatted_year}"
            if not categories_query
            else f"Dates importantes {Year.get_current().formatted_year} : " + ", ".join(category.title for category in categories)
        )

        def get(element: Occurrence, key: str) -> str:
            if key == "date":
                return format_date(element.start.date(), None if element.start.date() == element.end.date() else element.end.date())

            if key == "time":
                if element.event.time_text:
                    return element.event.time_text
                if not isinstance(element.start, datetime.datetime) or element.start.time() == datetime.time.min:
                    return ""
                return date(element.start.time(), "G:i") + (
                    " - " + date(element.end.time(), "G:i") if isinstance(element.end, datetime.datetime) else ""
                )

            if key == "name":
                return element.event.name

            if key == "place":
                return element.event.place

            raise ValueError(f"Invalid key: {key}")

        columns = {
            "date": capfirst(_("date")),
            "time": capfirst(_("time")),
            "name": capfirst(_("name")),
            "place": capfirst(_("place")),
        }

        occurrences = [
            Occurrence(date)
            for date
            in Date.objects.filter(categories__in=categories).distinct()
        ]

        table_data = [
            [*columns.values()],
            *([get(occurrence, column) for column in columns] for occurrence in occurrences),
        ]

        self.add_page()

        with self.use_font_face(FontFace(emphasis="B", size_pt=20)):
            self.multi_cell(0, 8, title, align=Align.C, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(self.font_size)

        Table(
            self,
            table_data,
            [40, 30, 60, 60],
            auto_line_height=True,
            line_height=self.font_size * 1.25,
            heading_line_height=self.font_size * 1.5,
            heading_font_face=FontFace(emphasis="B", fill_color=(255, 171, 145)),
            fill_font_face=FontFace(fill_color=238),
        ).render()
