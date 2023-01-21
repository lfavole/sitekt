import argparse
import datetime as dt
import getpass
import secrets
import sys
from pathlib import Path
from typing import Any, overload

sys.path.insert(0, str(Path(__file__).parent))
from utils import PYTHONANYWHERE, USERNAME, App, Settings, cprint, run  # pylint-ignore: C0413

FILE = Path(__file__).resolve()

def get_random_secret_key():
	"""
	Get a random Django secret key (extracted from `django.core.management.utils`).
	"""
	return "".join(secrets.choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)") for i in range(50))

def input_default(prompt: str, default: str | None = None, show = False):
	"""
	Ask for a string parameter (or show it). The returned value is a `str` (the parameter).
	"""
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
	"""
	Ask for a question (or show it without asking). The returned value is a `bool`.
	"""
	if show:
		print(prompt.rstrip() + " " + ("yes" if default else "no"))
		return default
	return input(prompt.rstrip() + " ") in TRUE_VALUES

def input_pass(prompt: str, default: str | None = None, show = False):
	"""
	Ask for a password (or show it). The returned value is a `str` (the password).
	"""
	if show:
		if default is None:
			raise ValueError("default parameter mustn't be None when show is true")
		print(prompt.rstrip() + ": ********")
		return default
	return getpass.getpass(prompt.rstrip() + ": ")

TRUE_VALUES = ("y", "yes", "true", "1")

apps = App.all()
DEFAULT_APP_NAME = str(apps[0])
DEFAULT_GITHUB_REPO = run("git remote get-url origin", True).stdout.strip().removesuffix(".git")

@overload
def create_settings_file(app_or_apps: list[App], settings: Settings | dict[str, Any] | None = None, interactive = True) -> list[Settings]:
	...

@overload
def create_settings_file(app_or_apps: App | None = None, settings: Settings | dict[str, Any] | None = None, interactive = True) -> Settings:
	...

def create_settings_file(app_or_apps: list[App] | App | None = None, settings: Settings | dict[str, Any] | None = None, interactive = True):
	"""
	Create the `settings.py` file interactively or not. Return the corresponding `Settings` object.
	"""
	cprint("Settings file creator", "blue")
	print()

	if settings is None:
		settings = {}

	if isinstance(app_or_apps, list):
		ret: list[Settings] = []
		for app in app_or_apps:
			ret.append(create_settings_file(app, settings, interactive))
		return ret

	def get_key(key: str):
		ret = settings.get(key)
		if not interactive and ret is None:
			raise ValueError(f"Setting {key} not provided")
		return ret

	def ask(prompt: str, variable: str, default: str | None = None, password = False):
		return (input_pass if password else input_default)(prompt, get_key(variable) or default, not interactive)

	now = dt.datetime.now()

	if app_or_apps:
		app = app_or_apps
		APP_NAME = str(app)
	else:
		APP_NAME = ask("App name", "APP_NAME", DEFAULT_APP_NAME)
		app = App(APP_NAME)

	if not app.folder.exists():
		cprint("The app folder " + str(app.folder) + " doesn't exist.", "red")
		print()
		return Settings()

	SETTINGS_FILE = app.folder / "settings.py"

	if SETTINGS_FILE.exists():
		cprint("The settings file " + str(SETTINGS_FILE) + " already exists; this program will replace it.", "red")
		print()

	file: list[str | tuple[str, Any]] = []

	file.append("# Settings (auto-generated on " + now.strftime("%Y-%m-%d %H:%M:%S") + " by scripts/" + FILE.name + ")")
	file.append("")

	def add_setting(name: str, value: Any = None):
		file.append((name, value))

	add_setting("APP_NAME", APP_NAME)
	add_setting("HOST", None if PYTHONANYWHERE else ask("Host", "HOST"))
	add_setting("DEBUG", ask("Debug mode", "DEBUG"))
	add_setting("SECRET_KEY", ask("Secret key", "SECRET_KEY", get_random_secret_key(), True))
	file.append("")

	USE_SQLITE = ask("Use SQLite", "USE_SQLITE").lower() in TRUE_VALUES
	add_setting("USE_SQLITE", USE_SQLITE)

	if not USE_SQLITE:
		add_setting("DB_HOST", None if PYTHONANYWHERE else ask("Database host", "DB_HOST"))
		add_setting("DB_NAME", ask("Database name" + (" (without " + USERNAME + "$ prefix)" if PYTHONANYWHERE else ""), "DB_NAME"))
		add_setting("DB_USER", None if PYTHONANYWHERE else ask("Database username", "DB_USER"))
		add_setting("DB_PASSWORD", ask("Database password", "DB_PASSWORD", None, True))
	else:
		add_setting("DB_HOST")
		add_setting("DB_NAME")
		add_setting("DB_USER")
		add_setting("DB_PASSWORD")

	file.append("")

	add_setting("GITHUB_REPO", ask("GitHub repo URL (without .git)", "GITHUB_REPO"))
	add_setting("GITHUB_WEBHOOK_KEY", ask("GitHub webhook key", "GITHUB_WEBHOOK_KEY", None, True))

	params: dict[str, Any] = {}

	with open(SETTINGS_FILE, "w") as f:
		for line in file:
			if isinstance(line, tuple):
				params[line[0]] = line[1]
				f.write(line[0] + " = " + repr(line[1]) + "\n")
			else:
				f.write(line + "\n")

	cprint("Settings file created", "green")
	return Settings(params)

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("APPS", nargs = "*", help = "App names (folders directly in the git repository)")
	parser.add_argument("--yes", "-y", "--no-interactive", action = "store_false", dest = "interactive", help = "Don't ask questions")
	args = parser.parse_args()

	create_settings_file(App.get_list_from_argparse(args.APPS), {}, args.interactive)
