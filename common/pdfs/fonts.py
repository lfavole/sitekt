import tempfile
from pathlib import Path

import requests

_fonts_paths: dict[str, str] = {}

def get_montserrat_font(style: str):
    if style in _fonts_paths and _fonts_paths[style].exists():
        return _fonts_paths[style]
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
    file = Path(tempfile.mktemp(".ttf"))
    file.write_bytes(req.content)
    _fonts_paths[style] = file
    return file
