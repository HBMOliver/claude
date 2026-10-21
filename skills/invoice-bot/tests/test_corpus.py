"""Accuracy on an independent corpus of realistic invoice PDFs (tests/corpus/make_corpus.py, needs reportlab).

Run directly for a per-file report:  python3 tests/test_corpus.py -v
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from helpers import COMPANY
from invoicebot import suppliers as S
from invoicebot import textract
from invoicebot.extract import extract

HERE = Path(__file__).resolve().parent
FIELDS = ('doc_type', 'supplier', 'invoice_number', 'amount', 'currency', 'issue_date', 'due_date', 'paid_date',
          'payment_method', 'paid_stamp')
MIN_ACCURACY = 0.9

try:
    import reportlab  # noqa: F401
    HAVE_REPORTLAB = True
except ImportError:
    HAVE_REPORTLAB = False


def supplier_ok(found, truth):
    if not found:
        return False
    f = S.core_key(found)
    return f in (S.core_key(truth), S.core_key(S.display_name(truth, hungarian=True)), S.core_key(S.strip_legal(truth)))


def compare(ex, t):
    out = {}
    for f in FIELDS:
        want = t.get('supplier_legal_name') if f == 'supplier' else t.get(f)
        got = ex.get(f)
        if f == 'supplier':
            ok = supplier_ok(got, want)
        elif f == 'amount':
            ok = got is not None and want is not None and Decimal(got) == Decimal(want)
        elif f == 'paid_stamp':
            ok = bool(got) == bool(want)
        elif f == 'doc_type':
            ok = got == want
        else:
            ok = (got or None) == (want or None)
        out[f] = (ok, got, want)
    return out


def run_corpus(out_dir):
    subprocess.run([sys.executable, str(HERE / 'corpus' / 'make_corpus.py'), '--out', str(out_dir)], check=True,
                   capture_output=True)
    truth = json.loads((Path(out_dir) / 'truth.json').read_text(encoding='utf-8'))
    results = []
    for t in truth:
        text, method = textract.pdf_text(Path(out_dir) / t['file'])
        ex = extract(text, {}, COMPANY)
        results.append((t, compare(ex, t)))
    return results


@unittest.skipUnless(HAVE_REPORTLAB and (HERE / 'corpus' / 'make_corpus.py').exists(), 'needs reportlab and the corpus')
class TestCorpus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix='invoicebot-corpus-')
        cls.results = run_corpus(cls.tmp)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_accuracy_per_field(self):
        report, worst = [], []
        for f in FIELDS:
            n = sum(1 for _, r in self.results if r[f][0])
            acc = n / len(self.results)
            report.append(f'{f:<16} {n:>3}/{len(self.results)}  {acc:.0%}')
            if acc < MIN_ACCURACY:
                worst.append(f)
        misses = [f"{t['file']}: {f} got {r[f][1]!r} want {r[f][2]!r}"
                  for t, r in self.results for f in FIELDS if not r[f][0]]
        if os.environ.get('CORPUS_REPORT') or '-v' in sys.argv:
            print('\n' + '\n'.join(report) + '\n' + '\n'.join(misses))
        self.assertFalse(worst, 'below {:.0%}: {}\n{}'.format(MIN_ACCURACY, worst, '\n'.join(misses)))


if __name__ == '__main__':
    unittest.main()
