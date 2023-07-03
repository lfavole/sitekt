import argparse
import json
from datetime import date
from pathlib import Path

import requests

DATA = Path(__file__).resolve().parent.parent / "data"


def main(args):
	req = requests.get(
		"https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-calendrier-scolaire/records",
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
	lens = [0, 0, 0]
	for item in data["results"]:
		data = (
			item["description"],
			item["start_date"].split("T", 1)[0],
			item["end_date"].split("T", 1)[0],
		)
		result.append(data)
		for i, element in enumerate(data):
			if lens[i] < len(element):
				lens[i] = len(element)

	for line in result:
		to_print = []
		for i, element in enumerate(line):
			to_print.append(element.ljust(lens[i]))

		print("  ".join(to_print))

	with open(DATA / "fr_holidays.json", "w") as f:
		json.dump(result, f)


def contribute_to_argparse(parser: argparse.ArgumentParser):
	parser.add_argument("START_YEAR", nargs="?", default=date.today().year, type=int, help="start year")
