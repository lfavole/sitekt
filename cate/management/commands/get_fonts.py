from pathlib import Path

from django.core.management.base import BaseCommand
import requests

DATA = Path(__file__).resolve().parent.parent / "data"
FONTS = DATA / "fonts"


class Command(BaseCommand):
    def handle(self, **_options):
        BASE_URL = "https://raw.githubusercontent.com/JulietaUla/Montserrat/master/fonts/ttf"
        for style in ["Regular", "Bold", "Italic", "BoldItalic"]:
            filename = "Montserrat-" + style + ".ttf"
            print("Downloading " + filename)
            url = BASE_URL + "/" + filename
            req = requests.get(url, stream=True)
            with open(FONTS / filename, "wb") as f:
                for chunk in req.iter_content(64 * 1024):
                    print("#", end="")
                    f.write(chunk)
            print()
