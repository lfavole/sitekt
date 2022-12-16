import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from common import PYTHONANYWHERE, run
import settings

if not PYTHONANYWHERE:
	sys.exit()

USERNAME = os.environ.get("USERNAME", "")

FOLDER = Path(__file__).parent / settings.APP_NAME
if not os.path.exists(FOLDER):
    os.makedirs(FOLDER, exist_ok = True)
os.chdir(FOLDER)

manage_py_args = [sys.executable, str(Path(__file__).parent.parent / "cate/manage.py")]

run("git init")
run(["git", "pull", settings.GITHUB_REPO + ".git", "main"])
run([*manage_py_args, "migrate"])
run([*manage_py_args, "migrate"])
print("OK")
