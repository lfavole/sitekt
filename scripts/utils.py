import getpass
import importlib
import os
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

APP_NAME = "cate"


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


def get_vars(obj: Any) -> dict[str, Any]:
	"""
	Return a `dict` (name, value) containing all the variables defined in the object (for example a module).
	"""
	return {name: getattr(obj, name) for name in dir(obj) if not name.startswith("__") and not name.endswith("__")}


def run(args: list[str] | str, pipe = False, capture = False, **kwargs) -> sp.CompletedProcess[str]:
	"""
	Run the command specified by args. Return a `CompletedProcess[str]`.

	`pipe=True` wraps the input and output in pipes.

	`capture=True` adds the command before the output, that is captured.
	"""
	# pylint: disable=W1510
	if isinstance(args, str):
		args = shlex.split(args)
	kwargs = {**kwargs, "encoding": "utf-8", "errors": "replace"}

	if pipe:
		kwargs["stdin"] = sp.PIPE
		kwargs["stdout"] = sp.PIPE
		kwargs["stderr"] = sp.PIPE
	if capture:
		kwargs["capture_output"] = True

	before_text = ""
	after_text = ""

	if not pipe or capture:
		before_text = "\n--- Command: " + " ".join(shlex.quote(arg) for arg in args) + " ---\n"
		if not capture:
			print(before_text, end="")

	ret = sp.run(args, **kwargs)

	if not pipe or capture:
		after_text = "--- End of command ---\n"
		if not capture:
			print(after_text, end="")

	if capture:
		ret.stdout = before_text + ret.stdout + after_text

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
	if os.environ.get("COLORED") == "0":
		return text

	global colorama_inited  # pylint: disable=C0103
	if not colorama_inited:
		try:
			from colorama import init
		except ImportError:
			print("Colorama is not installed, falling back to plain text")
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

def check_if_installed(module_name: str):
	"""
	Check that the `module_name` is installed and writes it.
	"""
	try:
		importlib.import_module(module_name)
	except ImportError:
		print(f"{module_name} is not installed")
	else:
		print(f"{module_name} is installed")
