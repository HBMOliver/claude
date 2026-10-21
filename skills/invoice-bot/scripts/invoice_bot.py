#!/usr/bin/env python3
"""Invoice bot launcher: python3 invoice_bot.py [--home DIR] COMMAND   (try: python3 invoice_bot.py --help)

The program lives in the invoicebot/ folder next to this file; it needs Python 3.9+ and, for reading
PDFs, poppler's pdftotext (best) or the pypdf package.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from invoicebot.cli import main  # noqa: E402

if __name__ == '__main__':
    main()
