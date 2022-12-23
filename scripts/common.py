import getpass
import importlib
import os
import re
import shlex
import subprocess as sp
import sys
from pathlib import Path
from typing import Any, TypeVar

Self = TypeVar("Self")

USERNAME = getpass.getuser()

PYTHONANYWHERE_SITE = os.environ.get("PYTHONANYWHERE_SITE", "")
PYTHONANYWHERE = PYTHONANYWHERE_SITE != ""

FOLDER = Path(__file__).resolve().parent
BASE_FOLDER = FOLDER.parent

def import_path(path: Path | str, module: str, package: str | None = None):
	"""
	Import the `module` that is in the specified `path` by adding and removing the `path` to `sys.path`.
	"""
	old_path = sys.path.copy()
	sys.path.append(str(path))
	try:
		return importlib.import_module(module, package)
	finally:
		sys.path = old_path

class Namespace(dict):
	"""
	Namespace that provides access to attributes with dot syntax: `ns["key"] == ns.key`.
	"""
	def __getattr__(self, attr):
		return self[attr]

	def __setattr__(self, attr, value):
		self[attr] = value

	def __delattr__(self, attr):
		del self[attr]

	def __repr__(self):
		return "<Namespace " + super().__repr__() + ">"

class Settings(Namespace):
	"""
	Settings object
	"""
	def __init__(self, *args, **kwargs):
		# pylint: disable=C0103
		super().__init__(*args, **kwargs)

		if not self:
			return

		self.HOST = self.HOST or (USERNAME + "." + PYTHONANYWHERE_SITE)

		if PYTHONANYWHERE:
			self.DB_NAME: str | None = USERNAME + "$" + self.DB_NAME if self.DB_NAME else None
			self.DB_HOST = (USERNAME + ".mysql." + PYTHONANYWHERE_SITE.replace("pythonanywhere.com", "pythonanywhere-services.com"))
			self.DB_USER = self.DB_USER or USERNAME

			self.PYTHONANYWHERE_SITE = PYTHONANYWHERE_SITE if PYTHONANYWHERE else None
			self.WSGI_FILE = None if not self.HOST else Path("/var/www") / (self.HOST.replace(".", "_").lower().strip() + "_wsgi.py")
		else:
			self.DB_NAME = None
			self.DB_HOST = None

			self.PYTHONANYWHERE_SITE = None
			self.WSGI_FILE = None

	@classmethod
	def create(cls: Self) -> Self:
		"""
		Create the settings with `create_settings.py` and return the created settings.

		Usage: `settings = settings.create()`
		"""
		create = import_path(FOLDER, "create_settings").create_settings_file
		return create()

def get_vars(obj: Any) -> dict[str, Any]:
	"""
	Return a `dict` (name, value) containing all the variables defined in the object (for example a module).
	"""
	return {name: getattr(obj, name) for name in dir(obj) if not name.startswith("__") and not name.endswith("__")}

class App:
	"""
	Object representing an app
	"""
	BASE_FOLDER = BASE_FOLDER

	def __init__(self, folder: str | Path):
		self.folder = (self.BASE_FOLDER / folder) if isinstance(folder, str) else folder
		self._settings = None

	@property
	def settings(self):
		"""
		Settings of the app
		"""
		if self._settings is not None:
			return self._settings

		try:
			settings_module = import_path(self.folder, "settings")
		except ImportError:
			self._settings = Settings()
		else:
			self._settings = Settings(get_vars(settings_module))
		return self._settings

	def __str__(self):
		return self.folder.name

	def __repr__(self):
		return "<App " + repr(str(self)) + ">"

	# Methods for comparing Apps with sorted() in App.all()
	def __lt__(self, other):
		return str(self) < str(other)

	def __gt__(self, other):
		return str(self) > str(other)

	def __eq__(self, other):
		return str(self) == str(other)

	# Shorthand for addition: print("Deleting app " + app + "...")
	def __add__(self, other):
		return str(self) + other

	def __radd__(self, other):
		return other + str(self)

	# Implementation of the slash: app / "manage.py"
	def __truediv__(self, other):
		return self.folder / other

	@classmethod
	def all(cls):
		"""
		Get all apps.
		"""
		return sorted(
			cls(path) for path in cls.BASE_FOLDER.glob("*/")
			if not path.name.startswith(".") # Don't include hidden folders like .vscode
			and path.name != "scripts" # Don't include scripts folder
			and not path.name.startswith("_") # Don't include __pycache__
		)

	@classmethod
	def get_list_from_argparse(cls, argument: list[str]):
		"""
		Get the `App` objects from an `argparse` list argument.
		"""
		return [cls(app) for app in argument]

	@classmethod
	def get_from_argparse(cls, argument: str | None):
		"""
		Get the `App` object from an `argparse` argument.
		"""
		if argument:
			return cls(argument)

		apps = cls.all()
		if not apps:
			cprint("No app could be found", "red")
			sys.exit()

		if len(apps) > 2:
			cprint("Multiple apps have been found:", "red")
			for app in apps:
				print("- " + app)
			cprint("Please choose an app from this list and provide it as the first argument.", "red")
			sys.exit()
		return apps[0]

def is_sensitive(key_name: str):
	"""
	Return True if the key name is the name of a sensitive information.
	"""
	sensitive_names = "API TOKEN KEY SECRET PASS SIGNATURE".split(" ")

	for name in sensitive_names:
		if name in key_name.upper():
			return True

	return False

def run(args: list[str] | str, pipe = False, **kwargs) -> sp.CompletedProcess[str]:
	"""
	Run the command specified by args. Return a `CompletedProcess[str]`.
	"""
	# pylint: disable=W1510
	if isinstance(args, str):
		args = shlex.split(args)
	kwargs = {**kwargs, "encoding": "utf-8", "errors": "replace"}
	if pipe:
		kwargs = {**kwargs, "stdin": sp.PIPE, "stdout": sp.PIPE, "stderr": sp.PIPE}
	if not pipe:
		print()
		print("--- Command: " + " ".join(shlex.quote(arg) for arg in args) + " ---")
	ret = sp.run(args, **kwargs)
	if not pipe:
		print("--- End of command ---")
		print()
	return ret


COLORS = ["grey", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
ATTRIBUTES = ["", "bold", "dark", "italic", "underline", "blink", "rapidblink", "reverse", "concealed", "strike"]

colorama_inited = sys.platform != "win32" # pylint: disable=C0103

def colored(text: str, color: str | None = None, on_color: str | None = None, attrs: list[str] | None = None):
	"""
	Colorize text.

	Available colors : grey, red, green, yellow, blue, magenta, cyan, white.

	Available attributes : bold, dark, underline, blink, reverse, concealed, strike

	Examples :
		colored("Hello world!", "red", "grey", ["bold", "blink"])
		colored("Hello world!", "green")
	"""
	global colorama_inited # pylint: disable=C0103
	if os.environ.get("COLORED") == "0":
		return text

	if not colorama_inited:
		try:
			from colorama import init
		except ImportError:
			install("colorama", "colorama")
		try:
			from colorama import init
		except ImportError:
			os.putenv("COLORED", "0")
			return text
		init()
		colorama_inited = True

	def get_color_code(color: str, background = False):
		color = color.lower()
		color_id = 3 # normal (dark) colors = 3x
		if color.startswith("light"):
			color = color.removeprefix("light")
			color_id = 9 # light colors = 9x
		elif color.startswith("dark"):
			color = color.removeprefix("dark")
		color = color.strip()
		if background:
			color_id += 1 # background colors = 3x -> 4x or 9x -> 10x
		return "\033[" + str(color_id) + str(COLORS.index(color)) + "m"

	final_text = ""
	if color is not None:
		final_text += get_color_code(color)
	if on_color is not None:
		final_text += get_color_code(on_color, True)
	if attrs is not None:
		for attr in attrs:
			final_text += "\033[" + str(ATTRIBUTES.index(attr)) + "m"
	return final_text + text + "\033[0m"

def cprint(text: str, color: str | None = None, on_color: str | None = None, attrs: list[str] | None = None, *args, **kwargs): # pylint: disable=W1113
	"""
	Print colored text. Shorthand for `print(colored(...))`.
	"""
	print(colored(text, color, on_color, attrs), *args, **kwargs)

def install(package: str, module_name: str):
	"""
	Install a package with `pip`. `package` is the pip package name and `module_name` is the module name to import.
	"""
	try:
		importlib.import_module(module_name)
	except ImportError:
		print("Installing " + package + "...")
		run([sys.executable, "-m", "pip", "install", package])
		print("Checking installation...")
		if run([sys.executable, "-c", "import " + module_name]).returncode != 0:
			print("Can't import " + package + " (import " + module_name + ")")
		else:
			print(package + " installed")
	else:
		print(package + " already installed")
	print()

def parse_packages_list(text: str) -> list[tuple[str, str, str]]:
	"""
	Parse a packages list (`requirements.txt` file). Return a list of tuples (package, version, comment)
	"""
	return re.findall(r"(.*?)\s*?([=<>~].*?)?\s*?(#\s*?.*?)?\n", text)
