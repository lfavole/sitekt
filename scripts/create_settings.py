import datetime as dt
import getpass
from pathlib import Path
import secrets
import sys
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from common import PYTHONANYWHERE, USERNAME, cprint, run

FILE = Path(__file__).resolve()
FOLDER = FILE.parent
SETTINGS_FILE = FOLDER / "settings.py"

def get_random_secret_key():
	return "".join(secrets.choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)") for i in range(50))

def input_default(prompt: str, default: str | None = None, show = False):
	if show:
		if default is None:
			raise ValueError("default parameter mustn't be None when show is true")
		print(prompt.rstrip() + ": " + default) # type: ignore
		return default
	if default is None:
		return input(prompt.rstrip() + ": ")
	ret = input(f"{prompt.rstrip()} [default: {default}]: ")
	if ret == "":
		return default
	return ret

def input_question(prompt: str, default = False, show = False):
	if show:
		print(prompt.rstrip() + " " + ("yes" if default else "no"))
		return default
	return input(prompt.rstrip() + " ") in TRUE_VALUES

def input_pass(prompt: str, default: str | None = None, show = False):
	if show:
		if default is None:
			raise ValueError("default parameter mustn't be None when show is true")
		print(prompt.rstrip() + ": ********")
		return default
	return getpass.getpass(prompt.rstrip() + ": ")

TRUE_VALUES = ("y", "yes", "true", "1")

DEFAULT_GITHUB_REPO = run("git remote get-url origin", True).stdout.strip().removesuffix(".git")

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

GITHUB_REPO = {input_default("GitHub repo URL (without .git)", get_key("GITHUB_REPO") or DEFAULT_GITHUB_REPO)!r}
"""

	with open(SETTINGS_FILE, "w") as f:
		f.write(settings_content)

	cprint("Settings file created", "green")

if __name__ == "__main__":
	create_settings_file()
