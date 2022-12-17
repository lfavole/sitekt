import os
import shlex
import subprocess as sp

from colorama import init

init()

PYTHONANYWHERE = os.environ.get("PYTHONANYWHERE_SITE", "") != ""

def is_sensitive(key_name: str):
	"""
	Return True if the key name is the name of a sensitive information.
	"""
	sensitive_names = "API TOKEN KEY SECRET PASS SIGNATURE".split(" ")

	for name in sensitive_names:
		if name in key_name.upper():
			return True

	return False

def run(args: list[str] | str, pipe = False):
	"""
	Run the command specified by args and show
	"""
	if isinstance(args, str):
		args = shlex.split(args)
	kwargs = {}
	if pipe:
		kwargs = {"stdin": sp.PIPE, "stdout": sp.PIPE, "stderr": sp.PIPE}
	if not pipe:
		print()
		print("--- Command: " + " ".join(shlex.quote(arg) for arg in args) + "---")
	ret = sp.run(args, **kwargs)
	if not pipe:
		print("--- End of command ---")
		print()
	return ret


COLORS = ["grey", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
ATTRIBUTES = ["", "bold", "dark", "italic", "underline", "blink", "rapidblink", "reverse", "concealed", "strike"]

def colored(text: str, color: str | None = None, on_color: str | None = None, attrs: list[str] | None = None):
	"""
	Colorize text.

	Available colors : grey, red, green, yellow, blue, magenta, cyan, white.

	Available attributes : bold, dark, underline, blink, reverse, concealed, strike

	Examples :
		colored("Hello world!", "red", "grey", ["blue", "blink"])
		colored("Hello world!", "green")
	"""
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
