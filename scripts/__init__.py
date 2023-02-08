import argparse
import importlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve()

def main():
    def sanitize(name):
        return name.removesuffix(".py").lower().strip().replace("-", "_")

    files = [
        sanitize(file.name)
        for file in HERE.parent.iterdir()
        if file.is_file()
    ]
    if HERE.name in files:
        files.remove(HERE.name)
    if "utils" in files:
        files.remove("utils")

    if len(sys.argv) < 2:
        print("Not enough arguments")
        sys.exit(1)

    subparser = sanitize(sys.argv[1])
    if subparser not in files:
        print(f"The file '{subparser}' doesn't exist.")
        sys.exit(1)

    module = importlib.import_module("." + subparser, __name__)

    parser = argparse.ArgumentParser()
    module.contribute_to_argparse(parser)

    args = parser.parse_args(sys.argv[2:])
    module.main(args)

if __name__ == "__main__":
    sys.path.insert(0, str(HERE.parent.parent))
    from scripts import main # type: ignore
    main()
