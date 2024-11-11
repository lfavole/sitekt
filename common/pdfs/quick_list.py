import re
from typing import Literal, Type

from django.apps import apps
from django.db import models
from django.http import HttpRequest
from django.utils.crypto import get_random_string
from fpdf.enums import AccessPermission, Align, XPos, YPos
from fpdf.fonts import FontFace

from ..models import CommonChild, Year
from . import PDF, Cell, Table


class CustomTable(Table):
    def _display_cell(self, cell: Cell, row_n: int, col_n: int, col_width: float, line_height: float, fill: bool):
        if row_n == 0:
            match = re.match(r"^(.*) (\(.*\))$", cell.text)
            if not match:
                super()._display_cell(cell, row_n, col_n, col_width, line_height, fill)
                return

            data = [
                (match[1], 16),
                (match[2], 9),
            ]
            font_size_total = sum(x[1] for x in data) + 2 * self.fpdf.c_margin
            x, y = self.fpdf.x, self.fpdf.y
            for i, (text, font_size) in enumerate(data):
                to_remove = self.fpdf.c_margin if i in (0, len(data) - 1) else 0
                with self.fpdf.use_font_face(FontFace(size_pt=font_size)):
                    self.fpdf.cell(
                        col_width,
                        line_height * (font_size + 2 * self.fpdf.c_margin - to_remove) / font_size_total,
                        text,
                        border="TLR" if i == 0 else "BLR",
                        align=self.align,
                        fill=fill,
                        new_x=XPos.LEFT,
                        new_y=YPos.NEXT,
                    )

            self.fpdf.x = x + col_width
            self.fpdf.y = y
            return

        if col_n == 0:
            x, y = self.fpdf.x, self.fpdf.y
            x2, y2 = x + col_width, y + line_height

            match = re.match(r"^(.*) -- (.*)$", cell.text)
            if not match and not cell.text:
                super()._display_cell(cell, row_n, col_n, col_width, line_height, fill)

            if not match:
                self.fpdf.line(x2, y, x, y2)
                return

            self.fpdf.cell(
                col_width,
                line_height,
                border=True,
                fill=fill,
                new_x=XPos.LEFT,
                new_y=YPos.TOP,
            )
            self.fpdf.line(x2, y, x, y2)

            self.fpdf.cell(
                col_width,
                line_height / 2,
                match[1],
                align=Align.L,
                new_x=XPos.LEFT,
                new_y=YPos.NEXT,
            )
            self.fpdf.cell(
                col_width,
                line_height / 2,
                match[2],
                align=Align.R,
            )

            self.fpdf.x = x + col_width
            self.fpdf.y = y
            return

        old_align = self.align
        if row_n > 0 and col_n == 2:
            self.align = Align.L
        super()._display_cell(cell, row_n, col_n, col_width, line_height, fill)
        self.align = old_align


class QuickList(PDF):
    lines: dict[str, int] = {}
    Child: Type[CommonChild]

    def __init__(self, *args, **kwargs):
        super().__init__("P", *args, **kwargs)

        self._classes_dict: dict[str, str] = {}

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

    filename = "liste_rapide"

    def render(self, app: Literal["espacecate", "aumonerie"], _request: HttpRequest):
        self.Child: Type[CommonChild] = self.get_model("Child")  # type: ignore
        fields: dict[str, tuple[str, int]] = {
            "groupe": ("", 25),
            "name": ("Enfants inscrits", 50),
            "frais": ("Participation (chèque - espèces - non payé)", 50),
            "signe": ("Autorisation (oui / non)", 39),
            "photos": ("Photos (oui / non)", 26),
        }
        a, b = sum(v for k, v in fields.values()), int(self.epw)
        assert a == b, f"{a} != {b}"
        field_types: dict[str, models.Field] = {}
        for field in self.Child._meta.fields:
            if field.name in fields and fields[field.name][0] == "":
                fields[field.name] = (field.verbose_name, fields[field.name][1])
                field_types[field.name] = type(field)

        self.page_title = (
            f"Liste des %s - %s - {Year.get_current().formatted_year}"
            % {
                "espacecate": ("enfants", "KT et EVF"),
                "aumonerie": ("jeunes", "Aumônerie"),
            }[app]
        )
        self.set_title(self.page_title)

        self.set_font("Montserrat")
        self.add_page()

        def get(element: CommonChild, key: str) -> str:
            if key == "name":
                return str(element)  # first name + last name

            if key == "groupe":
                classe = element.classe
                return (
                    (str(element.groupe) if element.groupe else "")
                    + " -- "
                    + (
                        (self.classes_dict.get(classe, classe) if app == "aumonerie" else classe)
                        if classe != "AUTRE"
                        else ""
                    )
                )

            ret = getattr(element, key)

            if key == "paye":
                return {
                    "oui": "Oui",
                    "non": "",
                    "attente": "",
                }[ret]

            if isinstance(ret, bool):
                return "Oui" if ret else ("Non" if key == "photos" else "")

            if isinstance(ret, int):
                return str(ret) + " €" if ret else ""

            return str(ret) if ret else ""

        childs = list(self.Child.objects.all())  # fetch the childs

        table_data: list[tuple[str, ...]] = [
            # ("Nom", "Prénom"),
            tuple(value[0] for value in fields.values()),
            *(tuple(get(element, key) for key in fields) for element in childs),
        ]
        empty_line = tuple([""] * len(fields))
        for _ in range(20 - len(table_data)):
            table_data.append(empty_line)

        table = CustomTable(
            self,
            table_data,
            [value[1] for value in fields.values()],
            heading_line_height=16,
            heading_font_face=FontFace(size_pt=16),
            font_face=FontFace(size_pt=13),
        )

        table.line_height = round((self.h - self.y - self.b_margin - table.heading_line_height) / 20, 1)
        table.render()

    def header(self):
        if self.page == 1:
            with self.local_context():
                self.set_font_size(22)
                self.cell(
                    0,
                    12,
                    self.page_title,
                    align=Align.C,
                    new_x=XPos.LMARGIN,
                    new_y=YPos.NEXT,
                )
                self.ln(3)
