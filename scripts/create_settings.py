import datetime as dt
import getpass
from pathlib import Path
import secrets
import sys
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from common import PYTHONANYWHERE, cprint, run

FILE = Path(__file__).resolve()
FOLDER = FILE.parent
SETTINGS_FILE = FOLDER / "settings.py"

def get_random_secret_key():
	return "".join(secrets.choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)") for i in range(50))

def input_default(prompt: str, default = None, show = False):
	if show:
		print(prompt.rstrip() + ": " + default)
		return
	if default is None:
		return input(prompt.rstrip() + ": ")
	ret = input(f"{prompt.rstrip()} [default: {default}]: ")
	if ret == "":
		return default
	return ret

def input_pass(prompt: str, default = None, show = False):
	if show:
		print(prompt.rstrip() + ": " + default)
		return
	return getpass.getpass(prompt.rstrip() + ": ")

TRUE_VALUES = ("y", "yes", "true", "1")

folders = sorted(
	path for path in FOLDER.parent.glob("*/")
	if not path.name.startswith(".")
	and path.name != "scripts"
	and not path.name.startswith("_")
)
DEFAULT_APP_NAME = folders[0].name
DEFAULT_GITHUB_REPO = run("git remote get-url origin", True).stdout.decode("utf-8", "replace").strip()

def create_settings_file(settings: dict[str, Any] = {}, interactive = True):
	"""
	Create the `settings.py` file interactively or not.
	"""
	def get_key(key: str):
		ret = settings.get(key)
		if not interactive:
			raise ValueError(f"Setting {key} not provided")
		return ret

	APP_NAME = ""

	cprint("Settings file creator", "blue")
	print()

	if SETTINGS_FILE.exists():
		cprint("The settings file " + str(SETTINGS_FILE) + " already exists; this program will replace it.", "red")
		print()

	settings_content = f"""\
# Settings (auto-generated on {dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} by scripts/{FILE.name})

APP_NAME = {(APP_NAME := input_default("App name", get_key("APP_NAME") or DEFAULT_APP_NAME, not interactive))!r}
HOST = {(None if PYTHONANYWHERE else input_default("Host", get_key("HOST"), not interactive))!r}
DEBUG = {(input_default("Debug mode", get_key("DEBUG"), not interactive) if not PYTHONANYWHERE else False)!r}
SECRET_KEY = {input_default("Secret key", get_key("SECRET_KEY") or get_random_secret_key(), not interactive)!r}
"""

	if get_key("USE_SQLITE") is True or input_default("Use SQLite").lower() in TRUE_VALUES:
		settings_content += f"""\

USE_SQLITE = True
"""
	else:
		settings_content += f"""\

USE_SQLITE = False
DB_HOST = {(None if PYTHONANYWHERE else input_default("Database host", get_key("DB_HOST"), not interactive))!r}
DB_NAME = {input_default("Database name", get_key("DB_NAME") or APP_NAME, not interactive)!r}
DB_USER = {(None if PYTHONANYWHERE else input_default("Database user", get_key("DB_USER"), not interactive))!r}
DB_PASSWORD = {input_pass("Database password", get_key("DB_PASSWORD"), not interactive)!r}
"""

	settings_content += f"""\

GITHUB_REPO = {input_default("GitHub repo URL", get_key("GITHUB_REPO") or DEFAULT_GITHUB_REPO)!r}
"""

	with open(SETTINGS_FILE, "w") as f:
		f.write(settings_content)

	cprint("Settings file created", "green")

if __name__ == "__main__":
	create_settings_file()
