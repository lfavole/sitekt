import getpass
import importlib
from pathlib import Path
import sys

from dotenv import set_key

sys.path.insert(0, str(Path(__file__).parent))
from common import PYTHONANYWHERE, cprint, run
import settings

def main():
	cprint("Configuration du site du caté Django", "blue")
	print()

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
				cprint("The host setting is required when we're not on a PythonAnywhere server.", "red")
				sys.exit()

		FOLDER = Path(__file__).resolve().parent / settings.APP_NAME

		with open("/var/www/" + settings.HOST.replace(".", "_").lower().strip() + "_wsgi.py", "w") as f:
			f.write(f"""\
		import sys
		sys.path.insert(0, {repr(str(FOLDER))})

		from {settings.APP_NAME}.wsgi import application
		""")

		env_file = FOLDER / ".env"
		def export_env_var(name, value):
			if "\\" in value:
				print("Antislash \\ detected in the " + name + " variable; there can be problems when loading this variable")
			set_key(env_file, PREFIX + "_" + name, value)

		export_env_var("HOST", settings.HOST)
		export_env_var("SECRET_KEY", settings.SECRET_KEY)

		export_env_var("MYSQL_NAME", USERNAME + "$" + settings.DB_NAME)
		export_env_var("MYSQL_USER", USERNAME)
		export_env_var("MYSQL_PASSWORD", settings.DB_PASSWORD)
		export_env_var("MYSQL_HOST", USERNAME + ".mysql.pythonanywhere-services.com")

	print("OK")

if __name__ == "__main__":
	main()
