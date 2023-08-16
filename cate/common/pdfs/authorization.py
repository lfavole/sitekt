import datetime as dt
from pathlib import Path
from typing import Any, Literal

from django.http import HttpRequest, QueryDict
from fpdf.enums import Align, XPos, YPos

from ..models import Year
from . import PDF

HERE = Path(__file__).resolve()
DATA = HERE.parent.parent.parent.parent / "data"

class AuthorizationData:
	"""
	Data that is used to render the authorization form.
	"""
	def __init__(self, data: dict[str, Any] | QueryDict | None = None):
		if data is None:
			data = {}

		parent_type: str = data.get("parent_type", "")
		if parent_type not in ("mother", "father", ""):
			parent_type = ""
		self.parent_type: Literal["mother", "father", ""] = parent_type  # type: ignore

		self.parent_name: str = data.get("parent_name", "")

		self.child_name: str = data.get("child_name", "")

		photos = data.get("photos")
		if photos is not None:
			if photos.lower() in ("false", "0"):
				photos = False
			else:
				photos = bool(photos)
		self.photos: bool | None = photos

		if self.parent_type or self.parent_name or self.child_name or self.photos:
			self.date = dt.date.today()
		else:
			self.date = None

class Authorization(PDF):
	line_h_mul = 1.9

	def __init__(self, request: HttpRequest, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.is_form_at_top = True

		self.add_font("Montserrat", "", str(DATA / "fonts/Montserrat-Regular.ttf"))
		self.add_font("Montserrat", "B", str(DATA / "fonts/Montserrat-Bold.ttf"))

		self.set_margin(7)
		self.set_auto_page_break(False)

		self.set_title("Autorisation et engagement")

	@property
	def font_size(self) -> float:
		return super().font_size  # type: ignore

	@property
	def line_h(self):
		return self.font_size * self.line_h_mul

	def write(self, h: float | None = None, txt: str = "", link: str = "", print_sh: bool = False) -> None:
		if h is None:
			h = self.line_h
		return super().write(h, txt, link, print_sh)

	def ln(self, h: float | None = None) -> None:
		if h is None:
			h = self.line_h
		return super().ln(h)

	def dash(self):
		length = self.line_h / 2
		self.line(self.x + length, self.y + length, self.x + length * 1.5, self.y + length)
		self.cell(length * 2)

	def checkbox(
		self,
		x: float | None = None,
		y: float | None = None,
		size: float | None = None,
		checked = False,
		style = "D",
	):
		if x is None:
			x = self.x
		if y is None:
			y = self.y + self.line_h / 2 - self.font_size / 2
		if size is None:
			size = self.font_size

		self.rect(x, y, size, size, style)
		if checked:
			p = self.line_width * 2  # space between the cell and the cross
			left = y + p
			right = y + size - p
			top = x + p
			bottom = x + size - p
			self.line(top, left, bottom, right)
			self.line(top, right, bottom, left)

	def render_section_title(self, title: str):
		self.set_font("", "B", 22)
		self.cell(0, self.line_h * 0.7, title, border = True, align = Align.C, new_x = XPos.LMARGIN, new_y = YPos.NEXT)
		self.ln(4)

		self.set_font("", "", 12)

	def render_line(self, text: str, value: str | None = None):
		self.write(txt = text)

		self.cell(self.get_string_width("  "))
		self.line(self.x, self.y + 6, self.w - self.l_margin, self.y + 6)
		if value:
			self.write(txt = value)

	def render_form(self, app: Literal["espacecate", "aumonerie"], data: AuthorizationData | None = None):
		if data is None:
			data = AuthorizationData()

		if self.is_form_at_top:
			self.add_page()
		else:
			self.line(0, self.y, self.w, self.y)
			self.ln(self.t_margin)

		self.is_form_at_top = not self.is_form_at_top

		self.set_font("Montserrat", "", 10)
		self.cell(0, txt = "Secteur paroissial de l'Embrunais et du Savinois", align = Align.L)
		title = {"espacecate": "Catéchisme", "aumonerie": "Aumônerie des Jeunes"}[app]
		self.cell(0, txt = f"{title} pour l'année scolaire {Year.get_current().formatted_year}", align = Align.R)
		self.ln(self.line_h * 1.5)

		self.render_section_title("Autorisation")

		self.render_line(
			"Je soussigné" + {
				"mother": "e",
				"father": "",
			}.get(data.parent_type, "(e)"),
			data.parent_name,
		)

		self.ln()
		self.write(txt = {
			"mother": "mère",
			"father": "père",
		}.get(data.parent_type, "père/mère") + " de l'enfant")

		self.cell(self.get_string_width("  "))
		self.line(self.x, self.y + 6, self.w - self.l_margin, self.y + 6)
		self.write(txt = data.child_name)

		self.ln()
		self.dash()
		text = {
			"espacecate": f"du catéchisme des Paroisses de l'Embrunais et du Savinois pour l'année scolaire {Year.get_current().formatted_year}",
			"aumonerie": "de l'Aumônerie des Jeunes",
	  	}[app]
		self.write(txt = f"autorise mon enfant à participer aux activités {text}.")
		self.ln()


		self.dash()
		self.cell(1)
		photos_param = data.photos
		photos = None if photos_param is None else bool(photos_param)

		self.checkbox(checked = photos is True)
		self.cell(5)
		self.write(txt = "autorise")

		self.cell(10)
		self.checkbox(checked = photos is False)
		self.cell(5)
		self.write(txt = "n'autorise pas")

		self.ln()
		text = {"espacecate": "du catéchisme", "aumonerie": "de l'Aumônerie"}[app]
		self.write(txt = f"la publication des photos de mon enfant prises au cours des différentes manifestations liées aux activités {text} (plaquettes, presse municipale et locale, site Internet, ...).")
		self.ln()
		self.ln(4)

		self.render_section_title("Engagement")

		self.write(txt = "Je m'engage :")

		lines = [
			f"à ce que mon enfant participe de manière régulière aux rencontres {text}",
			"à prévenir impérativement en cas d'absence",
		]
		if app == "aumonerie":
			lines.append("à ce que mon enfant n'utilise pas son téléphone portable pendant les rencontres")
		for line in lines:
			self.ln()
			self.dash()
			self.write(txt = line)

		self.ln()
		self.ln(4)

		self.write(txt = "Date :")
		self.cell(self.get_string_width(" ") + 1)

		attr: str
		zeros: int
		width: int
		for i, (attr, zeros, width) in enumerate([
			("day", 2, 10),
			("month", 2, 10),
			("year", 4, 15),
		]):
			if i > 0:
				self.cell(4, self.line_h, "/", align = Align.C)
			self.line(self.x, self.y + 6, self.x + width, self.y + 6)
			self.cell(width, self.line_h, str(getattr(data.date, attr)).rjust(zeros, "0") if data.date is not None else "", align = Align.C)

		self.cell(30)
		self.write(txt = "Signature(s) :")
		self.ln()
		self.ln()

def authorization_pdf(request: HttpRequest, app: Literal["espacecate", "aumonerie"]):
	pdf = Authorization(request)
	try:
		number = int(request.GET.get("exemplaires", 1))
	except ValueError:
		number = 1

	data = AuthorizationData(request.GET)
	for _ in range(number):
		pdf.render_form(app, data)
	return bytes(pdf.output())
