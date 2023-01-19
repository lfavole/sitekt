import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import BASE_FOLDER, PYTHONANYWHERE, App, cprint, install, parse_packages_list
from create_settings import input_question


def setup(apps: list[App], interactive = False):
	"""
	Set up the environment for the specified Django apps interactively or not.
	"""
	cprint("Configuration du site du caté Django", "blue")
	print()

	print("Installing modules (if they are not already installed)")

	with open(BASE_FOLDER / "requirements.txt") as f:
		requirements = f.read()

	# TODO: venv
	for package, version, comment in parse_packages_list(requirements):
		# Install Colorama only on Windows
		if sys.platform != "win32" and package == "colorama":
			continue
		# Don't install servers on PythonAnywhere
		if PYTHONANYWHERE:
			if package == "waitress" or package == "gunicorn":
				continue
		# Install Waitress (not Gunicorn) on Windows and Android (Termux)
		if (sys.platform == "win32" or hasattr(sys, "getandroidapilevel")) and package == "gunicorn":
			continue
		# Install Gunicorn (not Waitress) on non-Windows platforms
		if sys.platform != "win32" and package == "waitress":
			continue
		install(package + version, comment.removeprefix("#").strip())

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

	cprint("OK", "green")

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("APPS", nargs = "*", help = "App names (folders directly in the git repository)")
	parser.add_argument("--yes", "-y", "--no-interactive", action = "store_false", dest = "interactive", help = "Don't ask questions")
	args = parser.parse_args()

	setup(App.get_list_from_argparse(args.APPS), args.interactive)
