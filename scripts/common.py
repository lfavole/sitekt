import getpass
import importlib
import os
from pathlib import Path
import re
import shlex
import subprocess as sp
import sys
from typing import Self

USERNAME = getpass.getuser()

PYTHONANYWHERE_SITE = os.environ.get("PYTHONANYWHERE_SITE", "")
PYTHONANYWHERE = PYTHONANYWHERE_SITE != ""

FOLDER = Path(__file__).resolve().parent
BASE_FOLDER = FOLDER.parent

def import_path(path, module, package = None):
	"""
	Import the `module` that is in the specified `path` by adding and removing the `path` to `sys.path`.
	"""
	old_path = sys.path.copy()
	sys.path.clear()
	sys.path.append(path)
	try:
		return importlib.import_module(module, package)
	finally:
		sys.path = old_path

class Namespace(dict):
	def __getattr__(self, attr):
		return self[attr]

	def __setattr__(self, attr, value):
		self[attr] = value

	def __delattr__(self, attr):
		del self[attr]

	def __repr__(self):
		return "<Namespace " + super().__repr__() + ">"

class Settings(Namespace):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		if not self:
			return

		self.HOST = self.HOST or (USERNAME + "." + PYTHONANYWHERE_SITE)

		if PYTHONANYWHERE:
			self.DB_NAME = USERNAME + "$" + self.DB_NAME
			self.DB_HOST = (USERNAME + ".mysql." + PYTHONANYWHERE_SITE.replace("pythonanywhere.com", "pythonanywhere-services.com"))

			self.PYTHONANYWHERE_SITE = PYTHONANYWHERE_SITE if PYTHONANYWHERE else None
			self.WSGI_FILE = None if not self.HOST else Path("/var/www") / (self.HOST.replace(".", "_").lower().strip() + "_wsgi.py")

	@classmethod
	def create(cls) -> Self:
		create = import_path(FOLDER, "create_settings").create_settings_file
		return create()

class App:
	BASE_FOLDER = BASE_FOLDER

	def __init__(self, folder: str | Path):
		self.folder = BASE_FOLDER / folder if isinstance(folder, str) else folder
		self._settings = None

	@property
	def settings(self):
		if self._settings is not None:
			return self._settings

		try:
			settings_module = import_path(BASE_FOLDER, str(self) + ".settings")
		except ImportError:
			self._settings = Settings()
		else:
			self._settings = Settings(vars(settings_module))
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
		Get all `App`s.
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

colorama_inited = sys.platform != "win32"

def colored(text: str, color: str | None = None, on_color: str | None = None, attrs: list[str] | None = None):
	"""
	Colorize text.

	Available colors : grey, red, green, yellow, blue, magenta, cyan, white.

	Available attributes : bold, dark, underline, blink, reverse, concealed, strike

	Examples :
		colored("Hello world!", "red", "grey", ["bold", "blink"])
		colored("Hello world!", "green")
	"""
	global colorama_inited
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

def cprint(text: str, color: str | None = None, on_color: str | None = None, attrs: list[str] | None = None, *args, **kwargs):
	"""
	Print colored text. Shorthand for print(colored(...)).
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
	return re.findall(r"(.*?)\s*?([=<>~].*?)?\s*?(#\s*?.*?)?\n", text)
