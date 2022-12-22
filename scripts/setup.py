import argparse
import getpass
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from common import get_host, PYTHONANYWHERE, PYTHONANYWHERE_SITE, cprint, get_wsgi_file, install, parse_packages_list

def setup(interactive = False):
	cprint("Configuration du site du caté Django", "blue")
	print()

	if not (Path(__file__).resolve().parent / "settings.py").exists():
		cprint("The settings.py file doesn't exist: " + ("creating it" if interactive else "setup stopped"), "red")
		if not interactive:
			return
		else:
			from create_settings import create_settings_file
			create_settings_file()

	import settings

	print("Installing modules (if they are not already installed)")

	with open(Path(__file__).resolve().parent.parent / "requirements.txt") as f:
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

	if PYTHONANYWHERE:
		USERNAME = getpass.getuser()
		PREFIX = settings.APP_NAME.upper()

		HOST = get_host(settings)
		if HOST is None:
			cprint("The HOST setting is required when we're not on a PythonAnywhere server.", "red")
			return

		BASE_FOLDER = Path(__file__).resolve().parent.parent / settings.APP_NAME

		wsgi_file = get_wsgi_file(settings)
		print("Creating WSGI file " + wsgi_file)
		with open(wsgi_file, "w") as f:
			f.write(f"""\
import sys
sys.path.insert(0, {repr(str(BASE_FOLDER))})

from {settings.APP_NAME}.wsgi import application
""")

	cprint("OK", "green")

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--yes", "-y", "--no-interactive", action = "store_false", dest = "interactive", help = "Don't ask questions")
	args = parser.parse_args()
	interactive: bool = args.interactive

	setup(interactive)
