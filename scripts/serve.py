import argparse
import sys

from .fetch import fetch
from .utils import PYTHONANYWHERE, App, cprint, import_path, run


def serve(app: App, host = "0.0.0.0", port = 8080, dev = False, download = True):
	settings = app.settings

	if not settings:
		return

	if PYTHONANYWHERE:
		cprint("Can't serve the website with this script on a PythonAnywhere server", "red")
		print("Your website is available on https://" + settings.HOST)
		return

	if download:
		fetch()

	cprint("Serving script", "blue")
	print()

	if dev:
		print("Serving with Django development server")
		run([sys.executable, str(app / "manage.py"), "runserver", host + ":" + str(port)])
		return

	try:
		if hasattr(sys, "getandroidapilevel"):
			cprint("Android environment detected; Gunicorn is not working on Android", "red")
			raise ImportError
		import gunicorn  # type: ignore
		print("Serving with Gunicorn")
		proc = run([sys.executable, "-m", "gunicorn", settings.APP_NAME + ".wsgi", "-b", host + ":" + str(port)], cwd = app.folder)
		if proc.returncode == 0:
			return
	except ImportError:
		pass

	try:
		print("Serving with Waitress")
		from waitress import serve  # type: ignore
	except ImportError:
		pass
	else:
		application = import_path(app.folder / str(app), "wsgi").application
		serve(application, host = host, port = port)
		return

	cprint("gunicorn and waitress are not installed", "red")
	return

def main(args):
	serve(App.get_from_argparse(args.APP), args.host, args.port, args.dev, args.fetch)

def contribute_to_argparse(parser: argparse.ArgumentParser):
	parser.add_argument("APP", nargs = "?", help = "app to serve")
	parser.add_argument("--host", type = str, default = "0.0.0.0", help = "host to use for the server (default: %(default)s)")
	parser.add_argument("--port", type = int, default = 8080, help = "port to use for the server (default: %(default)s)")
	parser.add_argument("--dev", action = "store_true", help = "use the development server")
	parser.add_argument("--no-fetch", action = "store_false", dest = "fetch", help = "don't fetch changes before serving")
