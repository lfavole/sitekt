import argparse
import subprocess as sp

from .create_settings import input_question
from .get_fonts import get_fonts
from .utils import BASE_FOLDER, PYTHONANYWHERE, App, check_if_installed, cprint


def setup(apps: list[App], interactive = False):
	"""
	Set up the environment for the specified Django apps interactively or not.
	"""
	cprint("Configuration du site du caté Django", "blue")
	print()

	print("Installing modules (if they are not already installed)")
	requirements = BASE_FOLDER / "requirements.txt"
	sp.run(["pip", "install", "-r", str(requirements)], check=True)

	with open(requirements) as f:
		requirements = f.read()

	for line in requirements.splitlines():
		_, comment = line.rsplit("#", 1)
		check_if_installed(comment.strip())

	for app in apps:
		settings = app.settings
		if not settings:
			cprint("The app " + app + "doesn't have a settings.py file" + ("." if interactive else ", skipping it."), "red")
			if not interactive:
				continue
			answer = input_question("Do you want to create it?")
			if answer:
				settings = settings.create()
			else:
				cprint("Skipping app " + app, "red")
				continue
		print("Setting up app " + app)
		if PYTHONANYWHERE:
			if settings.HOST is None:
				cprint("The HOST setting is required when we're not on a PythonAnywhere server.", "red")
				return

			if settings.WSGI_FILE:
				print("Creating WSGI file " + str(settings.WSGI_FILE))
				with open(settings.WSGI_FILE, "w") as f:
					f.write(f"""\
import sys
sys.path.insert(0, {repr(str(app.folder))})

from {settings.APP_NAME}.wsgi import application
""")

	print("Getting fonts")
	get_fonts()

	cprint("OK", "green")

def main(args):
	setup(App.get_list_from_argparse(args.APP), args.interactive)

def contribute_to_argparse(parser: argparse.ArgumentParser):
	parser.add_argument("APP", nargs = "*", help = "App name (folder directly in the git repository)")
	parser.add_argument("--yes", "-y", "--no-interactive", action = "store_false", dest = "interactive", help = "Don't ask questions")
