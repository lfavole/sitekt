import importlib
import os
from pathlib import Path
import shlex
import sys

PYTHONANYWHERE = os.environ.get("PYTHONANYWHERE_SITE", "") != ""

if not PYTHONANYWHERE:
	sys.exit()

USERNAME = os.environ.get("USERNAME", "")

def install(package: str, module_name: str | None = None):
	if not module_name:
		module_name = package.lower()

	try:
		importlib.import_module(module_name)
	except ImportError:
		print("Installation de " + package + "...")
		os.system("pip install " + shlex.quote(package))
		if os.system("python -c " + shlex.quote("import " + module_name)) != 0:
			print("Impossible d'importer " + package + " (import " + module_name + ") après son installation")
		else:
			print(package + " installé")
	else:
		print(package + " déjà installé")

install("Django")
install("django-admin-sortable2", "adminsortable2")
install("python-dotenv", "dotenv")

HOST = USERNAME + ".pythonanywhere.com"
APP_NAME = "cate"
FOLDER = str(Path(__file__).resolve().parent / APP_NAME)

with open("/var/www/" + HOST.replace(".", "_") + "_wsgi.py", "w") as f:
	f.write(f"""\
import sys
sys.path.insert(0, {repr(FOLDER)})

from {APP_NAME}.wsgi import application
""")

with open(FOLDER + "/.env", "w") as f:
	def export_env_var(name, value):
		# os.system(f"export {name}=" + shlex.quote(value))
		f.write(name + "=" + value + "\n")

	export_env_var("DJANGO_HOST", HOST)
	export_env_var("DJANGO_SECRET_KEY", "jw0dfaz&#eybk^@d#y%(xdr23+f$q3gri4d3djea4ou2fc%l=&")

	export_env_var("DJANGO_MYSQL_NAME", USERNAME + "$django")
	export_env_var("DJANGO_MYSQL_USER", USERNAME)
	export_env_var("DJANGO_MYSQL_PASSWORD", "PyMySQL#05200")
	export_env_var("DJANGO_MYSQL_HOST", USERNAME + ".mysql.pythonanywhere-services.com")

print("OK")
