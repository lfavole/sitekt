from collections import defaultdict
from datetime import date
from typing import Iterable, Literal, Type

from django.apps import apps
from django.http import HttpRequest
from django.utils.crypto import get_random_string
from fpdf.enums import AccessPermission, Align, MethodReturnValue, StrokeCapStyle, XPos, YPos

from ..models import CommonChild, CommonGroup, CommonMeeting, Year  # pylint: disable=E0402
from . import PDF


class Meetings(PDF):
    MARKDOWN_LINK_COLOR = "#0d47a1"

    lines: dict[str, int] = {}
    Child: Type[CommonChild]

    def __init__(self, *args, **kwargs):
        super().__init__("L", *args, **kwargs)

        self._classes_dict: dict[str, str] = {}

        self.set_margin(5)
        self.set_auto_page_break(True, 5)

        self.set_encryption(  # type: ignore
            get_random_string(50),
            permissions=AccessPermission.PRINT_LOW_RES | AccessPermission.PRINT_HIGH_RES | AccessPermission.COPY,
        )

    @property
    def classes_dict(self):
        if self._classes_dict:
            return self._classes_dict

        for field in self.Child._meta.fields:
            if field.name == "classe":
                self._classes_dict = dict(field.choices)
                return self._classes_dict

        raise RuntimeError("Could not get the classes list for ordering")

    @property
    def classes(self):
        return list(self.classes_dict.keys())

    @property
    def filename(self):
        return self.Meeting._meta.verbose_name_plural

    def render(self, app: Literal["espacecate", "aumonerie"], request: HttpRequest):
        self.app = app
        self.black_white = bool(request.GET.get("black_white"))

        year = Year.get_current()

        Meeting: Type[CommonMeeting] = self.get_model("Meeting")  # type: ignore
        self.Meeting = Meeting
        Group: Type[CommonGroup] = self.get_model("Group")  # type: ignore

        meetings = list(Meeting.objects.prefetch_related("attendances"))
        groups: list[CommonGroup | None] = list(Group.objects.all())  # type: ignore
        groups.append(None)  # all groups

        meetings_for_tr: defaultdict[tuple[date, date], list[CommonMeeting]] = defaultdict(list)

        for meeting in meetings:
            for tr in year.trs:
                if tr[0] <= meeting.date < tr[1]:
                    meetings_for_tr[tr].append(meeting)
                break

        for i, tr in enumerate(year.trs, start=1):
            for group in groups:
                self.render_group(i, group, meetings_for_tr[tr])

    def _error_message(self, message: str):
        with self.local_context(font_size=10):
            self.cell(0, self.font_size, message, align=Align.C)

    def render_group(self, tr_n, group, meetings: list[CommonMeeting]):
        self.add_page()
        group_name = str(group) if group else "Tous les groupes"
        with self.local_context(font_style="BU", font_size=28):
            ordinal = str(tr_n) + ("er" if tr_n == 1 else "ème")
            self.cell(
                0,
                15,
                f"Rencontres – {group_name} – {ordinal} trimestre",
                align=Align.C,
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
            )

        if len(meetings) == 0:
            self._error_message("Aucune rencontre")
            return

        # the set removes duplicate elements
        # for the order: see sorted() 5 lines below
        childs: Iterable[CommonChild] = set()
        for meeting in meetings:
            childs_for_meeting: set[CommonChild] = {att.child for att in meeting.attendances.all()}  # type: ignore
            if group:
                childs.update(child for child in childs_for_meeting if child.groupe == group)
            else:
                childs.update(childs_for_meeting)

        if not childs:
            self._error_message("Aucun enfant")
            return

        # we don't need to sort by group, it's already done with the pages
        childs = sorted(childs, key=lambda c: c.official_name)

        start_y = self.y
        header_height = 15

        max_child_width = max(self.get_string_width(child.official_name) for child in childs) + 2 * self.c_margin

        col_width = min((self.epw - max_child_width) / len(meetings), 20)
        line_height = min((self.h - start_y - header_height - self.b_margin) / len(childs), 8)

        self.cell(max_child_width, header_height, border=True, new_x=XPos.LEFT, new_y=YPos.NEXT)
        for child in childs:
            self.cell(max_child_width, line_height, child.official_name, True, new_x=XPos.LEFT, new_y=YPos.NEXT)

        self.x += max_child_width

        meeting_kinds = {
            "MF": "MESSE",
            "AUMONERIE_COLLEGE": "Â COLLÈGE",
            "AUMONERIE_LYCEE": "Â LYCÉE",
        }
        for meeting in meetings:
            self.y = start_y
            meeting_name = (
                meeting.date.strftime("%d/%m")
                + "\n"
                + (meeting_kinds.get(meeting.kind, meeting.kind) or "AUTRE")
            )
            lines = self.multi_cell(
                col_width,
                header_height,
                meeting_name,
                dry_run=True,
                output=MethodReturnValue.LINES,
            )
            self.multi_cell(
                col_width,
                header_height / len(lines),
                # header_height / 2,
                meeting_name,
                True,
                align=Align.C,
                new_x=XPos.LEFT,
                new_y=YPos.NEXT,
            )
            for child in childs:
                try:
                    att = next(att for att in meeting.attendances.all() if att.child == child)  # type: ignore
                    self.draw_cell(col_width, line_height, att.is_present, att.has_warned)
                except StopIteration:
                    self.draw_cell(col_width, line_height, exists=False)

            self.x += col_width

    def draw_cell(
        self,
        col_width: float = 20,
        line_height: float = 8,
        present=None,
        warned=False,
        exists=True,
        example=False,
    ):
        horizontal = False
        vertical = False
        fill_color = None
        if exists:
            if present is True:
                fill_color = (100, 255, 100)
                horizontal, vertical = True, True  # "+" symbol
            elif present is False:
                fill_color = (255, 100, 100)
                horizontal, vertical = True, False  # "-" symbol
        else:
            fill_color = (255, 220, 100)

        x, y = self.x, self.y  # left x, top y
        cx, cy = x + col_width / 2, y + line_height / 2  # center x and y
        size = line_height * 0.3  # plus/minus/slash size

        if example:
            new_x, new_y = XPos.RIGHT, YPos.TOP
        else:
            new_x, new_y = XPos.LEFT, YPos.NEXT

        with self.local_context(fill_color=fill_color):
            self.cell(
                col_width,
                line_height,
                border=True,
                fill=bool(fill_color) and not self.black_white,
                new_x=new_x,
                new_y=new_y,
            )
        if horizontal or vertical:
            with self.local_context(line_width=0.6, stroke_cap_style=StrokeCapStyle.ROUND):
                if horizontal:
                    self.line(cx - size, cy, cx + size, cy)
                if vertical:
                    self.line(cx, cy - size, cx, cy + size)
        if warned:
            with self.go_back():
                self.x = x
                self.y = y + line_height - self.font_size
                self.cell(col_width, self.font_size, "P", align=Align.R)

    def footer(self):
        self.x = 5
        self.y = self.h - 12

        space_size = self.get_string_width(" ")

        legend = [
            ({"present": True}, "présent"),
            ({"present": False}, "absent"),
            ({"exists": False}, "non inscrit"),
            ({"warned": True}, "prévenu"),
        ]

        for kwargs, text in legend:
            self.draw_cell(**kwargs, example=True)
            self.cell(space_size)
            self.cell(h=8, txt=f"= {text}")
            self.cell(10)
