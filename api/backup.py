import datetime as dt
import os
import sys
import traceback
from http.server import BaseHTTPRequestHandler
from pathlib import Path

import django

sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cate.settings")
django.setup()

from django.core.mail import EmailMessage
from django.conf import settings

from cate.views import export


class FakeUser:
    @staticmethod
    def has_perm(*args, **kwargs):
        return True


class FakeRequest:
    user = FakeUser


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if os.environ.get("CRON_SECRET") and self.headers.get("Authorization", "") != f"Bearer {os.environ.get('CRON_SECRET', '')}":
            self.send_response(401)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Unauthorized")
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()

        _stdout_write = sys.stdout.write
        _stderr_write = sys.stderr.write

        def write(text):
            self.wfile.write(text.encode("utf-8"))
        sys.stdout.write = sys.stderr.write = write

        try:
            exported_data = export(FakeRequest, "json", "all", "all", "all").content
            email = EmailMessage(
                subject=f"Cate Backup for {dt.date.today().isoformat()}",
                body="Attached is the backup data.",
                to=[settings.DEFAULT_FROM_EMAIL],
            )
            email.attach(f"backup_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.json", exported_data, "application/json")
            email.send()
        except:
            traceback.print_exc(file=sys.stderr)
            return
        finally:
            sys.stdout.write = _stdout_write
            sys.stderr.write = _stderr_write

        self.wfile.write(b"OK")
