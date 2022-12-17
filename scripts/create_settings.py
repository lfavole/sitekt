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

def input_default(prompt: str, default = None):
	if default is None:
		return input(prompt.rstrip() + ": ")
	ret = input(f"{prompt.rstrip()} [default: {default}]: ")
	if ret == "":
		return default
	return ret

def input_pass(prompt: str):
	return getpass.getpass(prompt.rstrip() + ": ")

folders = sorted(
	path for path in FOLDER.parent.glob("*/")
	if not path.name.startswith(".") and path.name != "scripts"
)
DEFAULT_APP_NAME = folders[0].name
DEFAULT_GITHUB_REPO = run("git remote get-url origin", True).stdout.decode("utf-8", "replace").strip()

def create_settings_file(settings: dict[str, Any] = {}, interactive = True):
	"""
	Create the `settings.py` file interactively.
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
# Settings (auto-generated on {dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} by {FILE.name})

APP_NAME = {(APP_NAME := get_key("APP_NAME") or input_default("App name", DEFAULT_APP_NAME))!r}
HOST = {get_key("HOST") or (None if PYTHONANYWHERE else input_default("Host"))!r}
SECRET_KEY = {get_key("SECRET_KEY") or input_default("Secret key", get_random_secret_key())!r}

DB_NAME = {get_key("DB_NAME") or input_default("Database name", APP_NAME)!r}
DB_PASSWORD = {get_key("DB_PASSWORD") or input_pass("Database password")!r}

GITHUB_REPO = {get_key("GITHUB_REPO") or input_default("GitHub repo URL", DEFAULT_GITHUB_REPO)!r}
"""

	with open(SETTINGS_FILE, "w") as f:
		f.write(settings_content)

	cprint("Settings file created", "green")

if __name__ == "__main__":
	create_settings_file()
