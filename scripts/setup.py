import subprocess as sp
import sys

from .get_fonts import get_fonts
from .utils import APP_NAME, BASE_FOLDER, PYTHONANYWHERE, check_if_installed, cprint, import_path


def setup():
	"""
	Set up the environment for the specified Django apps interactively or not.
	"""
	cprint("Configuration du site du caté Django", "blue", attrs=["bold"])
	print()

	cprint("Installing modules (if they are not already installed)", "blue")
	requirements = BASE_FOLDER / "requirements.txt"
	sp.run([sys.executable, "-m", "pip", "install", "-r", str(requirements)], check=True)

	with open(requirements) as f:
		requirements = f.read()

	for line in requirements.splitlines():
		_, comment = line.rsplit("#", 1)
		check_if_installed(comment.strip())

	APP_FOLDER = BASE_FOLDER / APP_NAME
	if not (APP_FOLDER / "custom_settings_overrides.py").exists():
		cprint("The app doesn't have a custom_settings_overrides.py file. Please create one.", "red")
		return

	with import_path(APP_FOLDER, "custom_settings", remove_sys_path=False) as settings:
		cprint("Setting up app", "blue")
		if PYTHONANYWHERE:
			if settings.HOST is None:
				cprint("The HOST setting is required when we're not on a PythonAnywhere server.", "red")
				return

			if settings.WSGI_FILE:
				print("Creating WSGI file " + str(settings.WSGI_FILE))
				with open(settings.WSGI_FILE, "w") as f:
					f.write(f"""\
import sys
sys.path.insert(0, {repr(str(APP_FOLDER))})

from {APP_NAME}.wsgi import application
""")

	cprint("Getting fonts", "blue")
	get_fonts()

	cprint("OK", "green")

def main(args):
	setup()

def contribute_to_argparse(parser):
	pass
