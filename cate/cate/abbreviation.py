import re


def abbreviation(text: str):
    """
    Yields different reductions for a text.
    """
    ordinal = r"(\d+)([eè][rm]e?s?)?"  # creates \1 and \2
    article = r"(?:[dl](?:'|a|es?))\b"

    # remove common words
    text = re.sub(rf"\bpour {article}", "", text)
    text = re.sub(r"(?i)\b([dl]('|a|es?)|du|au|qu'|aux|ou|et|en|il)\b", "", text)

    # remove spaces
    text = re.sub(r"^\s+|\s+$", "", text)
    text = re.sub(r"\s{2,}", " ", text)

    # reduce words
    text = re.sub(r"\bpremi([eè]re?s?)\b", r"1\1", text)
    text = re.sub(r"\brencontres?\b", "renc.", text)
    text = re.sub(r"\bcommunions?\b", "com.", text)
    text = re.sub(r"\bassociations?\b", "asso.", text)
    text = re.sub(r"\bconfirm(?:ation|é)s?\b", "conf.", text)
    text = re.sub(r"\bcoll(?:ège|égiens)\b", "coll.", text)
    text = re.sub(r"\blycée(?:ns)?\b", "lyc.", text)

    text = re.sub(r"\bcaté(?:chisme)?\b", "KT", text)
    # "la" has already been removed
    text = re.sub(r"\béveil à foi\b", "EVF", text)

    ordinal_renc = ordinal + r" (?:renc\. |séance )?"
    text = re.sub(rf"{ordinal_renc}KT", r"KT \1", text)
    text = re.sub(rf"{ordinal_renc}EVF", r"EVF \1", text)
    text = re.sub(rf"{ordinal_renc}aumônerie", r"Aumônerie \1", text)

    yield text

    text = re.sub(ordinal, r"\1e", text)
    text = re.sub(r"\btemps fort\b", "TF", text)
    text = re.sub(r"\bmesse familles\b", "MF", text)
    text = re.sub(r"(?i)\bnotre[ -]dame\b", "ND", text)

    text = re.sub(r"\baccueil\b", "acc.", text)
    text = re.sub(r"\bnouveau(x?)\b", r"nv\1", text)

    yield text

    text = re.sub(r"(?i)\baumônerie\b", "â", text)

    yield text
