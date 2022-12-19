import getpass
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from common import PYTHONANYWHERE, cprint, get_host, get_wsgi_file, run
import settings

USERNAME = getpass.getuser()

FOLDER = Path(__file__).parent.parent
if not os.path.exists(FOLDER):
    os.makedirs(FOLDER, exist_ok = True)

manage_py_args = [sys.executable, str(FOLDER / settings.APP_NAME / "manage.py")]

def run_with_explanation(cmd: str | list[str], expl: str, cwd = FOLDER):
	print(expl[0].upper() + expl[1:])
	if run(cmd, cwd = cwd).returncode != 0:
		cprint("Error while " + expl, "red")

def fetch():
	cprint("Fetching script", "blue")
	print()

	run_with_explanation("git init", "creating git repo")
	run_with_explanation(["git", "pull", settings.GITHUB_REPO + ".git", "main"], "fetching changes")

	run_with_explanation([*manage_py_args, "migrate"], "migrating database")
	run_with_explanation([*manage_py_args, "collectstatic", "--noinput"], "collecting static files")

	if PYTHONANYWHERE:
		print("Touching WSGI file")
		Path(get_wsgi_file(settings)).touch()

	cprint("OK", "green")

if __name__ == "__main__":
	fetch()
