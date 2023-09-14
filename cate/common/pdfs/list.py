import datetime as dt
from typing import Literal, Type

from django.apps import apps
from django.db import models
from django.http import HttpRequest
from django.utils.crypto import get_random_string
from django.utils.formats import localize_input
from django.utils.numberformat import format as number_format
from fpdf.enums import AccessPermission, Align, XPos, YPos
from fpdf.fonts import FontFace

from ..models import CommonChild, Year
from . import PDF, Table


class List(PDF):
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
        "profession": ("date", "lieu"),
        "confirmation": ("date", "lieu"),
    }

    def get_sacrament(self, element: CommonChild, key: str):
        if not getattr(element, key):
            return "Non"

        ret = []
        for prefix in self.sacraments[key]:
            value = getattr(element, prefix + "_" + key)
            if not value:
                continue
            if prefix == "annee":
                ret.append("En " + str(value))
            elif prefix == "date":
                ret.append(localize_input(value))
            elif prefix == "lieu":
                ret.append("à " + value)
            else:
                ret.append(value)

        ret_str = "\n".join(ret)
        if not ret_str:
            return "Oui"
        return ret_str[0].upper() + ret_str[1:]

    def render(self, app: Literal["espacecate", "aumonerie"], regroup_by: str = ""):
        self.Child: Type[CommonChild] = apps.get_model(app, "Child")  # type: ignore
        fields: dict[str, tuple[str, int]] = {
            "espacecate": {
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
            },
            "aumonerie": {
                "nom": ("Nom", 23),  # same thing
                "prenom": ("", 20),
                "classe": ("", 15),
                "date_naissance": ("", 21),
                "adresse": ("", 40),
                "telephone": ("Téléphone", 35),
                "email": ("Email", 55),
                "bapteme": ("", 21),
                "premiere_communion": ("Première Comm.", 20),
                "profession": ("Prof. de foi", 19),
                "confirmation": ("Conf.", 18),
            },
        }[app]
        a, b = sum(v for k, v in fields.values()), int(self.epw)
        assert a == b, f"{a} != {b}"
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
                return self.classes_dict.get(ret, ret)

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

            heading_line_height = 10,
            heading_font_face = FontFace(size_pt = 10, fill_color = (34, 204, 34)),
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
