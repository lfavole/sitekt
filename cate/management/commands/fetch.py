import builtins
import io
import sys
from pathlib import Path
from shutil import which
from django.conf import settings

from django.core.management.base import BaseCommand

from .setup import Command as Setup
from .utils import run


class Command(BaseCommand):
    """
    Fetch changes with `git fetch` and migrate the projects.
    """

    def handle(self, pipe=False, **_options):
        outputs: list[str] = []

        if pipe:
            old_print = builtins.print

            def new_print(*args, file=None, **kwargs):
                if file in (sys.stdout, sys.stderr, None):
                    file = io.StringIO()
                    old_print(*args, **kwargs, file=file)
                    outputs.append(file.getvalue())
                else:
                    old_print(*args, **kwargs, file=file)

            builtins.print = new_print

        print("Fetching script")
        print()

        def _run_with_explanation(cmd: str | list[str], expl: str, cwd=settings.BASE_DIR):
            print(expl.capitalize())
            proc = run(cmd, capture=pipe, cwd=cwd)
            outputs.append(proc.stdout)
            if proc.returncode != 0:
                print("Error while " + expl)

        _run_with_explanation("git init", "creating git repo")
        _run_with_explanation(["git", "pull", settings.GITHUB_REPO + ".git"], "fetching changes")
        _run_with_explanation(["git", "stash"], "backing up changes")
        _run_with_explanation(["git", "reset", "--hard", "origin/main"], "resetting to server state")
        _run_with_explanation(["git", "pull", settings.GITHUB_REPO + ".git"], "re-fetching changes")

        if Path(sys.executable or "").name == "uwsgi":
            # use Python executable (not uwsgi) on PythonAnywhere
            sys.executable = which("python")

        Setup().handle()

        print("OK")

        if pipe:
            builtins.print = old_print
            return "".join(outputs)
