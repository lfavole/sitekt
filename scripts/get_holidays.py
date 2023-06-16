import argparse
from datetime import date
import json
from pathlib import Path

import requests

BASE_URL = "https://data.education.gouv.fr/api/v2/catalog/datasets/fr-en-calendrier-scolaire/exports/json"
DATA = Path(__file__).resolve().parent.parent / "data"


def main(args):
	req = requests.get(
		BASE_URL,
		{
			"select": "description,start_date,end_date",
			"where": (
				"location='Aix-Marseille' "
				f"AND start_date>=date'{args.START_YEAR}-07-01' "
				f"AND start_date<date'{args.START_YEAR + 1}-07-01' "
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


def contribute_to_argparse(parser: argparse.ArgumentParser):
	parser.add_argument("START_YEAR", nargs="?", default=date.today().year, type=int, help="start year")
