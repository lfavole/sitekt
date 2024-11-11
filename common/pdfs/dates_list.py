from typing import Literal

from common.models import CommonDate
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
        title = "Dates importantes"

        if app == "espacecate":
            from espacecate.models import Date
        elif app == "aumonerie":
            from aumonerie.models import Date

        def get(element: CommonDate, key: str) -> str:
            if key == "date":
                return format_date(element.start_date, element.end_date)

            if key == "time":
                if element.time_text:
                    return element.time_text
                return date(element.start_time, "G:i") + (
                    " - " + date(element.end_time, "G:i") if element.end_time else ""
                )

            return getattr(element, key)

        columns = {
            "date": capfirst(_("date")),
            "time": capfirst(_("time")),
            "name": capfirst(_("name")),
            "place": capfirst(_("place")),
        }

        table_data = [
            [*columns.values()],
            *([get(date, column) for column in columns] for date in Date.objects.all()),
        ]

        self.add_page()

        with self.use_font_face(FontFace(emphasis="B", size_pt=28)):
            self.cell(0, 12, title, align=Align.C, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
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
