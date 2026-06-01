import sys
from pathlib import Path

# Support both `python -m src` and `python src/__main__.py`
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    __package__ = "src"

from .cli import main

main()
