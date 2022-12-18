import getpass
from pathlib import Path
import sys

FOLDER = Path(__file__).parent
sys.path.insert(0, str(FOLDER))
from common import PYTHONANYWHERE, cprint, run
from fetch import fetch
import settings

BASE_DIR = FOLDER.parent / settings.APP_NAME

def serve(host = "0.0.0.0", port = 8080, dev = False):
	if PYTHONANYWHERE:
		cprint("Can't serve the website with this script on a PythonAnywhere server", "red")
		print("Your website is available on https://" + ((settings.HOST or getpass.getuser()) + ".pythonanywhere.com"))
		return

	fetch()

	cprint("Serving script", "blue")
	print()

	if dev:
		print("Serving with Django development server")
		run([sys.executable, str(BASE_DIR / "manage.py"), "runserver", host + ":" + str(port)])
		return

	try:
		print("Serving with Gunicorn")
		proc = run([sys.executable, "-m", "gunicorn", settings.APP_NAME + ".wsgi", "-b", host + ":" + str(port)], cwd = BASE_DIR)
		if proc.returncode == 0:
			return
	except ImportError:
		pass

	try:
		print("Serving with Waitress")
		from waitress import serve  # type: ignore
		sys.path.insert(0, str(FOLDER.parent / "cate"))
		import cate.wsgi  # type: ignore
		serve(cate.wsgi.application, host = host, port = port)
		return
	except ImportError:
		pass

	cprint("gunicorn and waitress are not installed", "red")
	return

if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser()
	parser.add_argument("--host", type = str, default = "0.0.0.0", help = "host to use for the server (default: %(default)s)")
	parser.add_argument("--port", type = int, default = 80, help = "port to use for the server (default: %(default)s)")
	parser.add_argument("--dev", action = "store_true", help = "use the development server")
	args = parser.parse_args()

	serve(args.host, args.port, args.dev)
