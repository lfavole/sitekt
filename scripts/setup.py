import argparse
import getpass
import importlib
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from common import PYTHONANYWHERE, cprint, run
import settings

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--yes", "-y", "--no-interactive", action = "store_false", dest = "interactive", help = "Don't ask questions")
	args = parser.parse_args()
	interactive: bool = args.interactive

	cprint("Configuration du site du caté Django", "blue")
	print()

	if not (Path(__file__).resolve().parent / "settings.py").exists():
		cprint("The settings.py file doesn't exist: " + ("creating it" if interactive else "setup stopped"), "red")
		if not interactive:
			sys.exit()
		else:
			from create_settings import create_settings_file
			create_settings_file()

	if not PYTHONANYWHERE:
		cprint("You're not on a PythonAnywhere server: setup stopped", "red")
		sys.exit()

	def install(package: str, module_name: str):
		"""
		Install a package with `pip`. `package` is the pip package name and `module_name` is the module name to import.
		"""
		if not module_name:
			module_name = package.lower()

		try:
			importlib.import_module(module_name)
		except ImportError:
			print("Installing " + package + "...")
			run([sys.executable, "-m", "pip", "install", package])
			print("Checking installation...")
			if run([sys.executable, "-c", "import " + package]).returncode != 0:
				print("Can't import " + package + "(import " + module_name + ")")
			else:
				print(package + " installed")
		else:
			print(package + " already installed")
		print()

	print("Installing modules (if they are not already installed)")

	install("Django", "django")
	install("django-admin-sortable2", "adminsortable2")
	install("python-dotenv", "dotenv")

	if PYTHONANYWHERE:
		USERNAME = getpass.getuser()
		PREFIX = settings.APP_NAME.upper()

		if settings.HOST is None:
			if PYTHONANYWHERE:
				settings.HOST = USERNAME + ".pythonanywhere.com"
			else:
				cprint("The HOST setting is required when we're not on a PythonAnywhere server.", "red")
				sys.exit()

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
	main()
