import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from common.models import Year
from fpdf import FPDF, FPDF_VERSION, output
from fpdf.drawing import DeviceRGB
from fpdf.enums import Align, CharVPos, MethodReturnValue, XPos, YPos
from fpdf.fonts import FontFace
from fpdf.line_break import Fragment
from fpdf.syntax import PDFDate, PDFObject, PDFString
from fpdf.table import Cell, Row  # noqa

HERE = Path(__file__).resolve()
DATA = HERE.parent.parent.parent.parent / "data"


@dataclass
class Table:
    fpdf: FPDF

    table_data: list[list[str]] = field(default_factory=list)
    col_widths: list[float] | float = field(default_factory=list)
    font_face: FontFace = field(default_factory=FontFace)
    line_height: float = 10
    align: Align = Align.C
    heading_font_face: FontFace = field(default_factory=FontFace)
    heading_line_height: float = 15

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
        line_height = self.heading_line_height if row_n == 0 else self.line_height

        if row_n > 0 and self.regroup_check:
            new_regrouped_data = self.regroup_check(row_n - 1)
            if new_regrouped_data != regrouped_data:
                regrouped_data = new_regrouped_data

                # check if the regrouped property AND the next line will trigger a page break
                # (don't leave the title alone at the bottom of the page...)
                if self.fpdf.will_page_break(self.regroup_height + line_height):
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
        if self.fpdf.will_page_break(line_height):
            # add a new page and print the header
            self.fpdf.add_page()
            fill, regrouped_data = self._display_line(0, fill, regrouped_data)

        font_face = self.font_face
        if fill:
            font_face_new = self.fill_font_face
            font_face_new.size_pt = font_face.size_pt
            font_face = font_face_new
        if row_n == 0:
            font_face = self.heading_font_face
            fill = bool(font_face.fill_color)

        with self.fpdf.use_font_face(font_face):
            col_n = 0
            for cell in data_row.cells:
                col_width = self._get_col_width(row_n, col_n, cell.colspan)
                self._display_cell(cell, row_n, col_n, col_width, line_height, fill)
                col_n += cell.colspan

            self.fpdf.ln(line_height)

        if self.fill_alternate:
            fill = not fill
        else:
            if row_n == 0:
                fill = False

        return fill, regrouped_data

    def _display_cell(self, cell: Cell, row_n: int, col_n: int, col_width: float, line_height: float, fill: bool):
        lines = self.fpdf.multi_cell(
            col_width,
            line_height,
            cell.text,
            dry_run = True,
            output = MethodReturnValue.LINES,
        )
        self.fpdf.multi_cell(
            col_width,
            line_height,
            cell.text,
            border = True,
            align = self.align,
            fill = fill,
            new_x = XPos.RIGHT,
            new_y = YPos.TOP,
            max_line_height = line_height / len(lines),
        )


class PDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_author("Secteur paroissial de l'Embrunais et du Savinois")
        self.set_creator(f"Espace caté {Year.get_current().formatted_year} (https://github.com/lfavole/sitekt)")
        self.set_producer(f"fpdf2 v{FPDF_VERSION} (https://github.com/PyFPDF/fpdf2)")

        self.set_margin(10)
        self.set_auto_page_break(True, 10)

        self.font_styles = [
            (r"((?<=[IVX]|\d)(?:e|er|ère|ème|nde)s?\b)", self._superscript),
            (r"((?:\+\d+ |\d)\d(?: \d\d){4})", self._phone_link),
            (r"([\w.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", self._email_link),
            # https://stackoverflow.com/a/3809435
            (r"(https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b[-a-zA-Z0-9@:%_\+.~#?&//=]*)", self._link),
        ]

    def _superscript(self, frag: Fragment):
        frag.graphics_state["char_vpos"] = CharVPos.SUP

    def _phone_link(self, frag: Fragment):
        self._link(frag)
        frag.link = "tel:" + "".join(c for c in frag.characters if c.isdigit() or c == "+")

    def _email_link(self, frag: Fragment):
        self._link(frag)
        frag.link = "mailto:" + frag.string

    def _link(self, frag: Fragment):
        frag.link = frag.string
        frag.graphics_state["underline"] = True
        if self.MARKDOWN_LINK_COLOR:
            frag.graphics_state["text_color"] = self.MARKDOWN_LINK_COLOR

    def _preload_font_styles(self, txt, markdown):
        """
        Apply all the font styles defined above (superscripts, phone numbers and email links).
        """
        frags: list[Fragment] = super()._preload_font_styles(txt, markdown)
        if len(frags) == 1 and not frags[0].characters:
            return frags

        for regexp, function in self.font_styles:
            ret = []
            for frag in frags:
                parts = re.split(regexp, frag.string)
                for i, part in enumerate(parts):
                    if not part:
                        continue
                    new_frag = Fragment(part, frag.graphics_state.copy(), frag.k, frag.link)
                    if i % 2 == 1:  # group captured by the split regex
                        function(new_frag)
                    ret.append(new_frag)
            frags = ret  # re-process the fragments

        return frags

    def set_font(self, family = None, style = "", size = 0) -> None:
        styles = {
            "": "Regular",
            "B": "Bold",
            "I": "Italic",
            "BI": "BoldItalic",
        }

        key_style = "".join(c for c in style.upper() if c in "BI")
        key_family = (family or self.font_family).lower()
        if key_family == "montserrat":
            key = key_family + key_style
            if key not in self.fonts:
                self.add_font(
                    key_family,
                    key_style,  # type: ignore
                    str(DATA / f"fonts/Montserrat-{styles[key_style]}.ttf"),
                )

        return super().set_font(family, style, size)


# Fix encryption of metadata (PyFPDF/fpdf2#865)

class PDFInfo(PDFObject):
    def __init__(
        self,
        title,
        subject,
        author,
        keywords,
        creator,
        producer,
        creation_date: PDFDate,
    ):
        super().__init__()
        self.title = PDFString(title, encrypt=True) if title else None
        self.subject = PDFString(subject, encrypt=True) if subject else None
        self.author = PDFString(author, encrypt=True) if author else None
        self.keywords = PDFString(keywords, encrypt=True) if keywords else None
        self.creator = PDFString(creator, encrypt=True) if creator else None
        self.producer = PDFString(producer, encrypt=True) if producer else None
        self.creation_date = creation_date


output.PDFInfo = PDFInfo
