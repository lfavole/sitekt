import datetime as dt
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Literal, Type

from django.apps import apps
from django.db import models
from django.http import HttpRequest
from django.utils.formats import localize_input
from django.utils.numberformat import format as number_format
from fpdf import FPDF
from fpdf.enums import AccessPermission, Align, MethodReturnValue, XPos, YPos
from fpdf.fonts import FontFace
from fpdf.table import Row

from ..models import CommonChild, Year

HERE = Path(__file__).resolve()
DATA = HERE.parent.parent.parent.parent / "data"


@dataclass
class Table:
    fpdf: FPDF

    table_data: list[list[str]] = field(default_factory=list)
    col_widths: list[float] | float = field(default_factory=list)
    line_height: float = 10
    align: Align = Align.C
    heading_font_face: FontFace = field(default_factory=FontFace)

    fill_alternate: bool = True
    fill_font_face: FontFace = field(default_factory=lambda: FontFace(fill_color = 230))

    regroup_check: Callable[[int], Any] | None = None
    regroup_font_face: FontFace = field(default_factory=FontFace)
    regroup_height: float = 7
    regroup_align: Align = Align.C

    rows: list[Row] = field(default_factory=list)

    def __post_init__(self):
        self.width = self.fpdf.epw  # FIXME

        for row in self.table_data:
            self.row(row)

    def row(self, cells=()):
        """
        Adds a row to the table. Returns a `Row` object.
        """
        row = Row(self.fpdf)
        self.rows.append(row)
        for cell in cells:
            row.cell(str(cell))
        return row

    def _get_col_width(self, row_n, col_n, colspan=1):
        if not self.col_widths:
            cols_count = self.rows[row_n].cols_count
            return colspan * (self.width / cols_count)
        if isinstance(self.col_widths, float):
            return colspan * self.col_widths
        if col_n >= len(self.col_widths):
            raise ValueError(
                f"Invalid .col_widths specified: missing width for table() column {col_n + 1} on row {row_n + 1}"
            )
        # pylint: disable=unsubscriptable-object
        col_width = 0
        col_ratio = self.width / sum(self.col_widths)
        for k in range(col_n, col_n + colspan):
            col_width += col_ratio * self.col_widths[k]
        return col_width

    def render(self):
        fill = False
        regrouped_data = object()

        for row_n in range(len(self.rows)):
            fill, regrouped_data = self._display_line(row_n, fill, regrouped_data)

    def _display_line(self, row_n, fill, regrouped_data):
        data_row = self.rows[row_n]

        if row_n > 0 and self.regroup_check:
            new_regrouped_data = self.regroup_check(row_n - 1)
            if new_regrouped_data != regrouped_data:
                regrouped_data = new_regrouped_data

                # check if the regrouped property AND the next line will trigger a page break
                # (don't leave the title alone at the bottom of the page...)
                if self.fpdf.will_page_break(self.regroup_height + self.line_height):
                    # add a new page and print the header
                    self.fpdf.add_page()
                    fill, regrouped_data = self._display_line(0, fill, regrouped_data)

                with self.fpdf.use_font_face(self.regroup_font_face):
                    self.fpdf.cell(
                        0,
                        self.regroup_height,
                        regrouped_data,
                        border = True,
                        align = self.regroup_align,
                        fill = True,
                        new_x = XPos.LMARGIN,
                        new_y = YPos.NEXT,
                    )
                fill = False

        # check if the next line will trigger a page break
        if self.fpdf.will_page_break(self.line_height):
            # add a new page and print the header
            self.fpdf.add_page()
            fill, regrouped_data = self._display_line(0, fill, regrouped_data)

        font_face = FontFace()
        if fill:
            font_face = self.fill_font_face
        if row_n == 0:
            font_face = self.heading_font_face
            fill = True

        with self.fpdf.use_font_face(font_face):
            col_n = 0
            for cell in data_row.cells:
                col_width = self._get_col_width(row_n, col_n, cell.colspan)
                lines = self.fpdf.multi_cell(
                    col_width,
                    self.line_height,
                    cell.text,
                    dry_run = True,
                    output = MethodReturnValue.LINES,
                )
                self.fpdf.multi_cell(
                    col_width,
                    self.line_height,
                    cell.text,
                    border = True,
                    align = self.align,
                    fill = fill,
                    new_x = XPos.RIGHT,
                    new_y = YPos.TOP,
                    max_line_height = self.line_height / len(lines),
                )
                col_n += cell.colspan

            self.fpdf.ln(self.line_height)

        if self.fill_alternate:
            fill = not fill
        else:
            if row_n == 0:
                fill = False

        return fill, regrouped_data

class List(FPDF):
    MARKDOWN_LINK_COLOR = "#0d47a1"

    lines: dict[str, int] = {}
    Child: Type[CommonChild]

    def __init__(self, *args, **kwargs):
        super().__init__("L", *args, **kwargs)

        self._classes: list[str] = []

        self.add_font("Montserrat", "", str(DATA / "fonts/Montserrat-Regular.ttf"))
        self.add_font("Montserrat", "B", str(DATA / "fonts/Montserrat-Bold.ttf"))

        self.set_margin(5)
        self.set_auto_page_break(True, 5)

        self.set_encryption(  # type: ignore
            "",
            AccessPermission.PRINT_LOW_RES | AccessPermission.PRINT_HIGH_RES | AccessPermission.COPY,
        )

    @property
    def classes(self):
        if self._classes:
            return self._classes

        for field in self.Child._meta.fields:
            if field.name == "classe":
                self._classes = [choice[1] for choice in field.choices]
                return self._classes

        raise RuntimeError("Could not get the classes list for ordering")

    def get_mother_father(self, element: CommonChild, key: str):
        real_key = "tel" if key == "telephone" else key
        ret = []
        for parent in ("mere", "pere"):
            value = getattr(element, f"{real_key}_{parent}")
            if not value:
                continue

            if key == "telephone":
                value = "0" + number_format(int(value), "", grouping = 2, thousand_sep = " ", force_grouping = True)
                if not int(value.replace(" ", "")):
                    return ""

            parent_formatted = {
                "mere": "mère",
                "pere": "père",
            }[parent]
            ret.append(f"{value} ({parent_formatted})")

        return "\n".join(ret)

    sacraments = {
        "bapteme": ("date", "lieu"),
        "pardon": ("annee",),
        "premiere_communion": ("date", "lieu"),
    }

    def get_sacrament(self, element: CommonChild, key: str):
        if not getattr(element, key):
            return "Non"

        ret = []
        for prefix in self.sacraments[key]:
            value = getattr(element, prefix + "_" + key)
            if prefix == "annee":
                ret.append("En " + str(value))
            elif prefix == "date":
                ret.append(localize_input(value))
            elif prefix == "lieu":
                ret.append("à " + value)
            else:
                ret.append(value)

        return "\n".join(ret).capitalize()

    def render(self, app: Literal["espacecate", "aumonerie"], regroup_by: str = ""):
        self.Child: Type[CommonChild] = apps.get_model(app, "Child")  # type: ignore
        fields: dict[str, tuple[str, int]] = {
            "nom": ("Nom", 23),  # not "Nom de famille" ! (too long)
            "prenom": ("", 20),
            "classe": ("", 15),
            "date_naissance": ("", 22),
            "adresse": ("", 40),
            "telephone": ("Téléphone", 35),
            "email": ("Email", 55),
            "bapteme": ("", 26),
            "pardon": ("", 24),
            "premiere_communion": ("", 27),
        }
        field_types: dict[str, models.Field] = {}
        for field in self.Child._meta.fields:
            if field.name in fields and fields[field.name][0] == "":
                fields[field.name] = (field.verbose_name, fields[field.name][1])
                field_types[field.name] = type(field)

        if regroup_by == "classe":
            del fields["classe"]
            # add +15 (width of the "class" column) to the address
            fields["adresse"] = (fields["adresse"][0], 55)

        self.page_title = {
            "espacecate": "Catéchisme",
            "aumonerie": "Aumônerie",
        }[app] + f" Embrun {Year.get_current().formatted_year}"
        self.set_title(f"Liste - {self.page_title}")

        self.add_page()
        self.set_font("Montserrat", "", 8)

        def get(element: CommonChild, key: str) -> str:
            if key in ("telephone", "email"):
                return self.get_mother_father(element, key)

            if key in self.sacraments:
                return self.get_sacrament(element, key)

            ret = getattr(element, key)
            if isinstance(ret, bool):
                return "Oui" if ret else "Non"
            if isinstance(ret, dt.date):
                return localize_input(ret)  # type: ignore

            if key == "classe":
                ret = str(ret).upper()
                return {
                    "PS": "Petite section",
                    "MS": "Moyenne section",
                    "GS": "Grande section",
                }.get(ret, ret)

            return str(ret)

        childs = self.Child.objects.all()

        regroup_check = None

        if regroup_by == "classe":
            regroup_check = lambda row_n: childs[row_n].classe
            childs = sorted(childs, key = lambda child: self.classes.index(child.classe))

        if regroup_by == "groupe":
            childs = childs.select_related("groupe")

            def get_group(child, sorting = True):
                # use "" when sorting so the childs appear at the top
                return child.groupe.name if child.groupe else ("" if sorting else "Aucun groupe")

            regroup_check = lambda row_n: get_group(childs[row_n], False)
            childs = sorted(childs, key = get_group)

        if regroup_by == "annees" and app == "espacecate":
            def get_years(child):
                classe = self.classes.index(child.classe)
                if classe <= 3:  # PS, MS, GS, CP
                    return -1
                return child.annees_kt or classe - 3

            def regroup_check(row_n):
                years = get_years(childs[row_n])
                if years == -1:
                    return "Éveil à la foi"
                return str(years) + ("ère" if years == 1 else "ème") + " année de caté"

            childs = sorted(childs, key = get_years)

        childs = list(childs)  # fetch the childs

        table_data: list[tuple[str, ...]] = [
            # ("Nom", "Prénom"),
            tuple(value[0] for value in fields.values()),
            *(tuple(get(element, key) for key in fields) for element in childs)
        ]

        Table(
            self,
            table_data,
            [value[1] for value in fields.values()],

            heading_font_face = FontFace(size_pt = 11, fill_color = (34, 204, 34)),
            regroup_check = regroup_check,
            regroup_font_face = FontFace(emphasis = "B", size_pt = 11, fill_color = (255, 68, 68)),
        ).render()

    def header(self):
        if self.page == 1:
            with self.local_context():
                self.set_font("Montserrat", "B", 14)
                self.set_fill_color(255, 193, 7)
                self.cell(
                    0,
                    10,
                    self.page_title,
                    border = True,
                    align = Align.C,
                    fill = True,
                    new_x = XPos.LMARGIN,
                    new_y = YPos.NEXT,
                )


def list_pdf(request: HttpRequest, app: Literal["espacecate", "aumonerie"]):
    pdf = List()
    pdf.render(app, request.GET.get("regroup", ""))
    return bytes(pdf.output())
