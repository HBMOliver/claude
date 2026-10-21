"""Shared test helpers: a throw-away bot in a temp folder, with a fixed 'today'."""
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / 'scripts'
sys.path.insert(0, str(SCRIPTS))
os.environ['INVOICEBOT_TODAY'] = '2026-10-21'

from invoicebot import db as dbm  # noqa: E402
from invoicebot import samples, suppliers  # noqa: E402
from invoicebot.config import Bot  # noqa: E402

COMPANY = {'name': 'HB Marketing Kft.', 'aliases': ['HB Marketing'], 'tax_ids': ['12345678-2-41', 'HU12345678'],
           'email_domains': ['hbmarketing.hu']}


def make_bot(tmp, company=None, **settings):
    bot = Bot(tmp, create=True)
    bot.user_config.update({'company': company or samples.DEMO_COMPANY})
    bot.user_config.update(settings)
    bot.save_config()
    bot = Bot(tmp)
    con = bot.db()
    try:
        with con:
            suppliers.seed_builtin(con)
    finally:
        con.close()
    return bot


class BotTestCase(unittest.TestCase):
    company = None
    settings = {}

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='invoicebot-test-')
        self.bot = make_bot(self.tmp, self.company, **self.settings)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def con(self):
        return self.bot.db()

    def inv(self, inv_id):
        con = self.bot.db()
        try:
            return dbm.get_invoice(con, inv_id)
        finally:
            con.close()

    def files(self):
        return sorted(str(p.relative_to(self.bot.archive)) for p in self.bot.archive.rglob('*')
                      if p.is_file() and p.name != '_summary.csv')
