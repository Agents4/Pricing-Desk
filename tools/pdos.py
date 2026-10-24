#!/usr/bin/env python3
"""Pricing Desk OS tool. Run `python3 tools/pdos.py --help`."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pdos.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
