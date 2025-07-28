import datetime as dt
from functools import lru_cache

import requests

@lru_cache
def get_holidays(start_year) -> list[tuple[str, dt.date, dt.date]]:
    req = requests.get(
        "https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-calendrier-scolaire/records",
        {
            "select": "description,start_date,end_date",
            "where": (
                "location='Aix-Marseille' "
                f"AND start_date>=date'{start_year}-07-01' "
                f"AND start_date<date'{start_year + 1}-07-01' "
                "AND (population='-' OR population='Élèves')"
            ),
            "limit": -1,
            "offset": 0,
            "timezone": "Europe/Paris",
        },
    )
    data = req.json()

    return [
        (
            item["description"],
            dt.datetime.fromisoformat(item["start_date"]).date(),
            dt.datetime.fromisoformat(item["end_date"]).date(),
        )
        for item in data["results"]
    ]
