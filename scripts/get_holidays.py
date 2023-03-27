import json
from pathlib import Path

import requests

BASE_URL = "https://data.education.gouv.fr/api/v2/catalog/datasets/fr-en-calendrier-scolaire/exports/json"
DATA = Path(__file__).resolve().parent.parent / "data"

start_year = 2023

def main(_args):
	req = requests.get(
		BASE_URL,
		{
			"select": "description,start_date,end_date",
			"where": (
				"location='Aix-Marseille' "
				f"AND start_date>=date'{start_year}-01-07' "
				f"AND start_date<date'{start_year + 1}-01-07' "
				"AND (population='-' OR population='Élèves')"
			),
			"limit": -1,
			"offset": 0,
			"timezone": "Europe/Paris",
		}
	)
	data = req.json()
	result: list[tuple[str, str, str]] = []
	for item in data:
		print(
			item["description"],
			item["start_date"].split("T", 1)[0],
			item["end_date"].split("T", 1)[0],
		)
		result.append((
			item["description"],
			item["start_date"].split("T", 1)[0],
			item["end_date"].split("T", 1)[0],
		))

	with open(DATA / "fr_holidays.json", "w") as f:
		json.dump(result, f)

def contribute_to_argparse(_parser):
	pass
