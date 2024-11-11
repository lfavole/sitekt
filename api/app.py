import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from cate.wsgi import application as app  # noqa
