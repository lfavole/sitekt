import datetime
from typing import Any

months = (
    "janvier",
    "février",
    "mars",
    "avril",
    "mai",
    "juin",
    "juillet",
    "août",
    "septembre",
    "octobre",
    "novembre",
    "décembre",
)


def fr_date_from_obj(d: Any) -> str:
    if not d:
        return ""
    if isinstance(d, str):
        # expect YYYY-MM-DD
        parts = d.split("-")
        if len(parts) >= 3:
            try:
                day = int(parts[2])
                month = int(parts[1])
                year = int(parts[0])
                return f"{day} {months[month-1]} {year}"
            except Exception:
                return d
        return d
    if isinstance(d, datetime.datetime) or isinstance(d, datetime.date):
        return f"{d.day} {months[d.month-1]} {d.year}"
    return str(d)


def format_time_obj(t: Any) -> str:
    if not t:
        return ""
    if isinstance(t, str):
        return t[:5]
    if isinstance(t, datetime.time):
        return t.strftime("%H:%M")
    return str(t)[:5]


def generate_default_site_message(name: str | None, start_date: Any, start_time: Any, end_time: Any) -> str:
    name = (name or "").strip()
    name_lower = name.lower()

    if name_lower.startswith("caté") or name_lower.startswith("cate"):
        base = "rencontre de caté"
        article = "La"
        past = "déplacée"
    elif name_lower.startswith("aumon"):
        base = "rencontre d'aumônerie"
        article = "La"
        past = "déplacée"
    else:
        if "messe" in name_lower:
            base = name or "messe"
            article = "La"
            past = "déplacée"
        elif any(k in name_lower for k in ("camp", "séjour", "colonie")):
            base = name or "événement"
            article = "Le"
            past = "déplacé"
        elif any(k in name_lower for k in ("rencontre", "temps fort", "profession", "confirmation")):
            base = name or "rencontre"
            article = "La"
            past = "déplacée"
        else:
            base = name or "événement"
            article = "Le"
            past = "déplacé"

    date_part = fr_date_from_obj(start_date)
    st = format_time_obj(start_time)
    et = format_time_obj(end_time)
    if st and et:
        times = f"de {st} à {et}"
    elif st:
        times = f"à {st}"
    else:
        times = ""

    head = f"{article} {base} du {date_part}" if date_part else f"{article} {base}"
    if times:
        return f"{head} est {past} {times}."
    return f"{head} est {past}."


def _norm(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, (datetime.date, datetime.datetime)):
        return v.isoformat()
    if isinstance(v, datetime.time):
        return v.strftime("%H:%M")
    if isinstance(v, str):
        return v
    return str(v)


def detect_date_modified(orig, data: dict) -> bool:
    # data usually contains strings (from dynamic admin JS). Normalize then compare
    for k in ("name", "start_date", "end_date", "start_time", "end_time", "place", "cancelled"):
        if _norm(getattr(orig, k, None)) != _norm(data.get(k)):
            return True
    return False
