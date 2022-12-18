import argparse
import getpass
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from common import PYTHONANYWHERE, PYTHONANYWHERE_SITE, cprint, install, parse_packages_list, run

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

	# if not PYTHONANYWHERE or True:
		# cprint("You're not on a PythonAnywhere server: setup stopped", "red")
		# return

	print("Installing modules (if they are not already installed)")

	with open(Path(__file__).resolve().parent.parent / "requirements.txt") as f:
		requirements = f.read()

	for package, version, comment in parse_packages_list(requirements):
		install(package + version, comment.removeprefix("#").strip())
	if sys.platform == "win32":
		install("waitress", "waitress")
	else:
		install("gunicorn", "gunicorn")

	if PYTHONANYWHERE:
		USERNAME = getpass.getuser()
		PREFIX = settings.APP_NAME.upper()

		if settings.HOST is None:
			if PYTHONANYWHERE:
				settings.HOST = USERNAME + "." + PYTHONANYWHERE_SITE
			else:
				cprint("The HOST setting is required when we're not on a PythonAnywhere server.", "red")
				return

		BASE_FOLDER = Path(__file__).resolve().parent / settings.APP_NAME

		wsgi_file = "/var/www/" + settings.HOST.replace(".", "_").lower().strip() + "_wsgi.py"
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
