import argparse
import builtins
import io
import sys
from pathlib import Path

from .utils import App
from .utils import cprint as old_cprint
from .utils import run

FOLDER = Path(__file__).parent.parent

def fetch(apps: list[App] | None = None, pipe = False):
	"""
	Fetch changes with `git fetch` and migrate the projects.
	"""
	outputs: list[str] = []

	if pipe:
		old_print = builtins.print

		def new_print(*args, file = None, **kwargs):
			if file in (sys.stdout, sys.stderr, None):
				file = io.StringIO()
				old_print(*args, **kwargs, file = file)
				outputs.append(file.getvalue())
			else:
				old_print(*args, **kwargs, file = file)

		builtins.print = new_print

		def cprint(text, *args, **kwargs):
			new_print(text)
	else:
		cprint = old_cprint  # because of namespace

	cprint("Fetching script", "blue")
	print()

	def _run_with_explanation(cmd: str | list[str], expl: str, cwd = FOLDER):
		print(expl.capitalize())
		proc = run(cmd, capture = pipe, cwd = cwd)
		outputs.append(proc.stdout)
		if proc.returncode != 0:
			cprint("Error while " + expl, "red")

	for app in apps or App.all():
		print("App " + app)
		settings = app.settings
		if not settings:
			cprint("Can't load settings for app " + app, "red")
			continue

		# _run_with_explanation("git init", "creating git repo")
		# _run_with_explanation(["git", "pull", settings.GITHUB_REPO + ".git"], "fetching changes")
		# _run_with_explanation(["git", "stash"], "backing up changes")
		# _run_with_explanation(["git", "reset", "--hard", "origin/main"], "resetting to server state")
		# _run_with_explanation(["git", "pull", settings.GITHUB_REPO + ".git"], "re-fetching changes")

		manage_py_args = [sys.executable, str(app / "manage.py")]

		# _run_with_explanation([*manage_py_args, "migrate"], "migrating database")
		# _run_with_explanation([*manage_py_args, "compilemessages"], "compiling translations")
		_run_with_explanation([*manage_py_args, "collectstatic", "--noinput"], "copying static files")

		if settings.WSGI_FILE:
			print("Touching WSGI file for app " + app)
			Path(settings.WSGI_FILE).touch()

	cprint("OK", "green")

	if pipe:
		builtins.print = old_print
		return "".join(outputs)

def main(args):
	fetch(App.get_list_from_argparse(args.APP))

def contribute_to_argparse(parser: argparse.ArgumentParser):
	parser.add_argument("APP", nargs = "*", help = "App name (folders directly in the git repository)")
