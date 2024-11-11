import shlex
import subprocess as sp
import threading
from functools import wraps
from typing import Callable, TypeVar


FunctionT = TypeVar("FunctionT", bound=Callable)

def run_in_thread(func: FunctionT) -> FunctionT:
    """Run a function in a thread."""

    @wraps(func)
    def decorator(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()

    return decorator  # type: ignore


def run(args: list[str] | str, pipe=False, capture=False, **kwargs) -> sp.CompletedProcess[str]:
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
