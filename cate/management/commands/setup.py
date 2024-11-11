import os
from pathlib import Path
import subprocess as sp
import sys
from django.conf import settings

from django.core.management.base import BaseCommand

from .get_fonts import Command as GetFonts
from .utils import run_in_thread


class Command(BaseCommand):
    """
    Set up the environment for the specified Django apps.
    """
    def handle(self, **_options):
        manage = [sys.executable, str(settings.BASE_DIR / "manage.py")]

        run_command_in_thread = run_in_thread(sp.run)

        if not os.environ.get("VERCEL"):
            print("Installing modules...")
            requirements = settings.BASE_DIR / "requirements.txt"
            sp.run([sys.executable, "-m", "pip", "install", "-r", str(requirements)], check=True)

        if os.environ.get("PYTHONANYWHERE"):
            print("Installing MySQL...")
            sp.run(["python3", "-m", "pip", "install", "mysqlclient~=2.2"], check=True)
        # we don't need to install psycopg if on Vercel (it's already installed by build.sh)

        def compile_translations():
            if os.environ.get("VERCEL"):
                print("Installing gettext...")
                sp.run(["dnf", "install", "-y", "gettext"], check=True)
            print("Compiling translations...")
            sp.run(
                [
                    *manage,
                    "compilemessages",
                    "--ignore",
                    "adminsortable2",
                    "--ignore",
                    "debug_toolbar",
                    "--ignore",
                    "django",
                ],
                check=True,
            )

        run_in_thread(compile_translations)()
        print("Collecting static files...")
        run_command_in_thread([*manage, "collectstatic", "--noinput", "--clear", "-v", "1"], check=True)

        print("Getting fonts...")
        run_in_thread(GetFonts().handle)()

        print("Creating the cache tables...")
        run_command_in_thread([*manage, "createcachetable"], check=True)
        print("Migrating...")
        run_command_in_thread([*manage, "migrate"], check=True)

        wsgi_file = "/var/www/" + os.environ.get("HOST", "").replace(".", "_").lower().strip() + "_wsgi.py"
        if os.environ.get("PYTHONANYWHERE") and wsgi_file:
            print("Touching WSGI file...")
            Path(wsgi_file).touch()

        print("OK")
