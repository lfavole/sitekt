import builtins
import io
import sys
from pathlib import Path
from shutil import which

from .setup import setup
from .utils import APP_NAME, BASE_FOLDER
from .utils import cprint as old_cprint
from .utils import import_path, run


def fetch(pipe = False):
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

	def _run_with_explanation(cmd: str | list[str], expl: str, cwd = BASE_FOLDER):
		print(expl.capitalize())
		proc = run(cmd, capture = pipe, cwd = cwd)
		outputs.append(proc.stdout)
		if proc.returncode != 0:
			cprint("Error while " + expl, "red")

	APP_FOLDER = BASE_FOLDER / APP_NAME
	if not (APP_FOLDER / "custom_settings_overrides.py").exists():
		cprint("The app doesn't have a custom_settings_overrides.py file. Please create one.", "red")
		return

	settings = import_path(APP_FOLDER, "custom_settings")

	_run_with_explanation("git init", "creating git repo")
	_run_with_explanation(["git", "pull", settings.GITHUB_REPO + ".git"], "fetching changes")
	_run_with_explanation(["git", "stash"], "backing up changes")
	_run_with_explanation(["git", "reset", "--hard", "origin/main"], "resetting to server state")
	_run_with_explanation(["git", "pull", settings.GITHUB_REPO + ".git"], "re-fetching changes")

	if Path(sys.executable or "").name == "uwsgi":
		# use Python executable (not uwsgi) on PythonAnywhere
		sys.executable = which("python")

	setup()

	manage_py_args = [sys.executable, str(APP_FOLDER / "manage.py")]

	_run_with_explanation([*manage_py_args, "migrate"], "migrating database")
	_run_with_explanation([*manage_py_args, "compilemessages"], "compiling translations")
	_run_with_explanation([*manage_py_args, "collectstatic", "--noinput"], "copying static files")

	if settings.WSGI_FILE:
		print("Touching WSGI file for app " + APP_NAME)
		Path(settings.WSGI_FILE).touch()

	cprint("OK", "green")

	if pipe:
		builtins.print = old_print
		return "".join(outputs)

def main(args):
	fetch()

def contribute_to_argparse(parser):
	pass
