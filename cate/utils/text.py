import re

from unidecode import unidecode


def slugify(text):
    """
    Return a slugified version of the given text, suitable for file names or page URLs.
    """
    text = unidecode(text.lower())
    text = text.replace("_", "-")
    text = re.sub(r"[^\w.]+", "-", text)
    text = re.sub(r"-{2,}", "-", text)
    text = text.replace("-.", ".").replace(".-", ".")
    text = text.strip("-")
    return text
