import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import App, cprint, run

FOLDER = Path(__file__).parent.parent
if not os.path.exists(FOLDER):
    os.makedirs(FOLDER, exist_ok = True)

def _run_with_explanation(cmd: str | list[str], expl: str, cwd = FOLDER):
	print(expl[0].upper() + expl[1:])
	if run(cmd, cwd = cwd).returncode != 0:
		cprint("Error while " + expl, "red")

def fetch(apps: list[App] | None = None):
	"""
	Fetch changes with `git fetch` and migrate the projects.
	"""
	cprint("Fetching script", "blue")
	print()

	for app in apps or App.all():
		print("App " + app)
		settings = app.settings
		if not settings:
			cprint("Can't load settings for app " + app, "red")
			continue

		_run_with_explanation("git init", "creating git repo")
		_run_with_explanation(["git", "pull", "--depth=1", "--rebase", settings.GITHUB_REPO + ".git", "main"], "fetching changes")

		manage_py_args = [sys.executable, str(app / "manage.py")]

		_run_with_explanation([*manage_py_args, "migrate"], "migrating database")
		_run_with_explanation([*manage_py_args, "collectstatic", "--noinput"], "collecting static files")

		if settings.WSGI_FILE:
			print("Touching WSGI file for app " + app)
			Path(settings.WSGI_FILE).touch()

	cprint("OK", "green")

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("APPS", nargs = "*", help = "App names (folders directly in the git repository)")
	args = parser.parse_args()

	fetch(App.get_list_from_argparse(args.APPS))
