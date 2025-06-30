import tempfile
from pathlib import Path

import requests

def get_montserrat_font(style: str):
    styles = {
        "": "Regular",
        "B": "Bold",
        "I": "Italic",
        "BI": "BoldItalic",
    }
    real_style = styles.get(str(style).upper(), "Regular")
    BASE_URL = "https://raw.githubusercontent.com/JulietaUla/Montserrat/master/fonts/ttf"
    req = requests.get(f"{BASE_URL}/Montserrat-{real_style}.ttf", stream=True)
    req.raise_for_status()
    file = tempfile.mktemp(".ttf")
    Path(file).write_bytes(req.content)
    return file
