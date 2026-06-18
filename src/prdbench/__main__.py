"""Entry point for running the PRDBench server: python -m src.prdbench [port]"""

import logging
import sys

from .server import run_server
from .config import DEFAULT_PORT, DEFAULT_HOST


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    host = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_HOST
    run_server(host, port)


if __name__ == "__main__":
    main()
