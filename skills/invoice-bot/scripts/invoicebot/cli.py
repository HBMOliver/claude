"""Command line: invoice_bot.py [--home DIR] COMMAND ...   (run with --help for the list)."""
import argparse
import getpass
import json
import os
import platform
import shutil
import sys
from pathlib import Path

from . import __version__
from . import auth
from . import bank
from . import collect
from . import db as dbm
from . import export
from . import pipeline as P
from . import suppliers as S
from .config import Bot, DEFAULTS, default_home
from .util import jdump, money, today, to_date


def _bot(a, create=False):
    return Bot(a.home, create=create)


def _out(a, obj, text):
    if getattr(a, 'json', False):
        print(json.dumps(obj, ensure_ascii=False, indent=1, default=str))
    else:
        print(text)


def _fmt_row(inv):
    paid = 'paid' if inv['paid'] else 'UNPAID' if inv['status'] == 'filed' else inv['status'].upper()
    return (f"#{inv['id']:<5} {inv.get('payment_date') or '----------'}  {paid:<9} "
            f"{(inv.get('supplier') or '?')[:28]:<28} {(inv.get('invoice_number') or '?')[:22]:<22} "
            f"{money(inv.get('amount'), inv.get('currency')):>16}  {inv['file_path']}")


# ------------------------------------------------------------------ setup
def cmd_init(a):
    home = Path(a.home).expanduser() if a.home else default_home()
    cfg_path = home / 'invoicebot.json'
    if cfg_path.exists() and not a.force:
        bot = Bot(home)
        print(f'Already set up: {cfg_path} (use --force to overwrite the settings given here).')
    else:
        bot = Bot(home, create=True)
    uc = bot.user_config
    comp = uc.setdefault('company', {})
    if a.company:
        comp['name'] = a.company
    if a.alias:
        comp['aliases'] = sorted(set(comp.get('aliases', [])) | set(a.alias))
    if a.tax_id:
        comp['tax_ids'] = sorted(set(comp.get('tax_ids', [])) | set(a.tax_id))
    if a.domain:
        comp['email_domains'] = sorted(set(comp.get('email_domains', [])) | {d.lower() for d in a.domain})
    if a.currency:
        uc['default_currency'] = a.currency.upper()
    if a.archive:
        uc['archive_dir'] = a.archive
    if a.csv_locale == 'hu' or a.csv_locale == 'eu':
        uc['csv'] = {'delimiter': ';', 'decimal': ','}
    elif a.csv_locale == 'en':
        uc['csv'] = {'delimiter': ',', 'decimal': '.'}
    uc.setdefault('archive_dir', DEFAULTS['archive_dir'])
    bot.save_config()
    bot = Bot(home)
    con = bot.db()
    try:
        with con:
            n = S.seed_builtin(con)
    finally:
        con.close()
    print(f'Invoice bot ready in {bot.home}')
    print(f'  settings : {bot.config_path}')
    print(f'  inbox    : {bot.inbox}   (drop invoices here)')
    print(f'  archive  : {bot.archive}')
    if n:
        print(f'  {n} well-known suppliers loaded (Google, Meta, Microsoft, ...)')
    if not bot.company.get('name'):
        print('  NOTE: set your company so it is never taken for the supplier:\n'
              f'        invoice_bot.py --home "{bot.home}" init --company "Your Company Kft." --tax-id 12345678-2-42')
    con = bot.db()
    try:
        if not auth.list_users(con):
            print(f'  Next: create an admin login:  invoice_bot.py --home "{bot.home}" users add <name>')
    finally:
        con.close()


def cmd_config(a):
    bot = _bot(a)
    if a.key is None:
        print(json.dumps(bot.cfg, ensure_ascii=False, indent=2))
        return
    if a.value is None:
        node = bot.cfg
        for k in a.key.split('.'):
            node = node[k]
        print(json.dumps(node, ensure_ascii=False, indent=2))
        return
    try:
        value = json.loads(a.value)
    except ValueError:
        value = a.value
    try:
        bot.set_option(a.key, value)
    except ValueError as e:
        print(f'ERROR: {e}')
        return 1
    print(f'{a.key} = {json.dumps(value, ensure_ascii=False)}')
    if a.key.split('.')[0] in ('naming', 'folders', 'payment'):
        n, errors = P.refile_all(bot)
        print(f'Re-filed {n} invoices with the new setting.')
        for e in errors:
            print(f'  ERROR {e} (run "verify --fix" once the cause is gone)')


def cmd_check(a):
    import importlib.util
    from . import textract
    pypdf_state = 'missing (pip install pypdf)'
    if importlib.util.find_spec('pypdf'):
        import pypdf
        ver = tuple(int(x) for x in pypdf.__version__.split('.')[:2] if x.isdigit())
        pypdf_state = f'ok ({pypdf.__version__})' if ver >= (3, 17) else \
            f'old ({pypdf.__version__}): pip install -U "pypdf>=3.17" so tables keep their columns'
    st = {'python': platform.python_version(), 'invoicebot': __version__,
          'pdftotext': shutil.which('pdftotext') or 'missing (install poppler-utils for the best results)',
          'pypdf': pypdf_state,
          'ocr (tesseract)': shutil.which('tesseract') or 'not installed (scanned invoices go to review)'}
    if not shutil.which('pdftotext') and not importlib.util.find_spec('pypdf'):
        st['WARNING'] = 'no PDF text extractor: install poppler-utils or pypdf'
    try:
        bot = _bot(a)
        st['home'] = str(bot.home)
        st['archive'] = str(bot.archive)
        st['company'] = bot.company.get('name') or 'NOT SET'
        if bot.cfg['imap'].get('enabled'):
            ok, msg = collect.imap_test(bot)
            st['imap'] = msg
    except FileNotFoundError as e:
        st['home'] = str(e)
    print(json.dumps(st, ensure_ascii=False, indent=1))


# ------------------------------------------------------------------ daily use
def cmd_status(a):
    bot = _bot(a)
    con = bot.db()
    try:
        q = lambda sql, *p: con.execute(sql, p).fetchone()[0]
        total = q('SELECT count(*) FROM invoices')
        filed = q("SELECT count(*) FROM invoices WHERE status = 'filed' AND paid = 1")
        unpaid = dbm.find_invoices(con, "status = 'filed' AND paid = 0", order='payment_date')
        review = q("SELECT count(*) FROM invoices WHERE status = 'review'")
        last = dbm.meta_get(con, 'last_run')
        users = auth.list_users(con)
        months = export.months(con)[:3]
        t = today().isoformat()
        overdue = [i for i in unpaid if i['due_date'] and i['due_date'] < t]
        obj = {'home': str(bot.home), 'archive': str(bot.archive), 'invoices': total, 'paid_and_filed': filed,
               'unpaid': len(unpaid), 'overdue': len(overdue), 'review': review, 'last_run': last,
               'admins': len(users), 'imap': bot.cfg['imap'].get('enabled'),
               'recent_months': [{'month': m, 'count': c, 'totals': {k: str(v) for k, v in tot.items()}}
                                 for m, c, tot in months]}
        lines = [f'Invoice bot: {bot.home}', f'Archive: {bot.archive}',
                 f'Invoices: {total} in the ledger, {filed} paid and filed by payment month']
        for m, c, tot in months:
            lines.append(f'  {m}: {c} paid  ' + ', '.join(money(v, k) for k, v in sorted(tot.items())))
        lines.append(f'Waiting for payment: {len(unpaid)}' + (f' ({len(overdue)} overdue)' if overdue else ''))
        lines.append(f'Need review: {review}')
        if last:
            c = last['counts']
            lines.append(f"Last collection: {last['finished'][:16].replace('T', ' ')} UTC - {c['new']} new, "
                         f"{len(last['errors'])} errors")
        else:
            lines.append('Last collection: never (run: invoice_bot.py run)')
        lines.append(f"IMAP: {'on, ' + bot.cfg['imap']['username'] if bot.cfg['imap'].get('enabled') else 'off'}"
                     f"   Admin users: {len(users)}   Company: {bot.company.get('name') or 'NOT SET'}")
        _out(a, obj, '\n'.join(lines))
    finally:
        con.close()


def cmd_run(a):
    bot = _bot(a)
    rep = collect.run(bot, inbox=not a.no_inbox, imap=not a.no_imap, actor='cli')
    if rep is None:
        print('Another collection run is in progress; nothing done.')
        return 1
    _out(a, rep.as_dict(), rep.text())
    return 1 if rep.errors else 0


def cmd_add(a):
    bot = _bot(a)
    rep = collect.Report()
    meta = {k: v for k, v in (('sender', a.sender), ('subject', a.subject)) if v}
    for f in a.files:
        p = Path(f)
        if not p.is_file():
            rep.error(f, 'no such file')
            continue
        collect.process_blob(bot, p.read_bytes(), p.name, a.source, dict(meta), rep, require_invoice=False)
    P._write_summaries(bot, rep.touched)
    _out(a, rep.as_dict(), rep.text())
    return 1 if rep.errors else 0


def _filters(a):
    where, params = [], []
    st = a.status or 'all'
    if st == 'unpaid':
        where.append("status = 'filed' AND paid = 0")
    elif st == 'paid':
        where.append("status = 'filed' AND paid = 1")
    elif st != 'all':
        where.append('status = ?')
        params.append(st)
    if a.month or a.year:
        where.append('payment_date LIKE ?')
        params.append((a.month or a.year) + '%')
    if a.supplier:
        where.append('supplier LIKE ?')
        params.append(f'%{a.supplier}%')
    if a.search:
        where.append('(supplier LIKE ? OR invoice_number LIKE ? OR original_name LIKE ? OR amount LIKE ?)')
        params += [f'%{a.search}%'] * 4
    return ' AND '.join(where) or '1=1', params


def cmd_list(a):
    bot = _bot(a)
    con = bot.db()
    try:
        where, params = _filters(a)
        invs = dbm.find_invoices(con, where, params, limit=a.limit)
        for i in invs:
            i.pop('text', None)
            i.pop('extracted', None)
        text = '\n'.join(_fmt_row(i) for i in invs) or 'No invoices match.'
        if invs and not a.json:
            tot = {}
            for i in invs:
                if i['amount']:
                    from decimal import Decimal
                    tot[i['currency']] = tot.get(i['currency'], Decimal(0)) + Decimal(i['amount'])
            text += f'\n{len(invs)} invoices. Total: ' + ', '.join(money(v, k) for k, v in sorted(tot.items()))
        _out(a, invs, text)
    finally:
        con.close()


def cmd_show(a):
    bot = _bot(a)
    con = bot.db()
    try:
        inv = dbm.get_invoice(con, a.id)
        if not inv:
            print(f'No invoice #{a.id}')
            return 1
        inv['events'] = dbm.events(con, a.id, 20)
        inv['file'] = str(bot.archive / inv['file_path'])
        if not a.text:
            inv.pop('text', None)
        if a.json:
            print(json.dumps(inv, ensure_ascii=False, indent=1, default=str))
            return 0
        ex = inv['extracted'] or {}
        lines = [f"Invoice #{inv['id']}  [{inv['status']}{', paid' if inv['paid'] else ', not paid yet' if inv['status'] == 'filed' else ''}]",
                 f"  file         {inv['file']}",
                 f"  original     {inv['original_name']}  (from {inv['source']})"]
        for k in ('supplier', 'invoice_number', 'amount', 'currency', 'issue_date', 'fulfilment_date', 'due_date',
                  'payment_method', 'payment_date', 'payment_source', 'doc_type', 'supplier_tax_id'):
            v = inv.get(k)
            if k == 'amount':
                v = money(v, inv.get('currency'))
            if k == 'payment_source':
                v = P.SOURCE_LABELS.get(v, v)
            mark = ' (set by admin)' if k in (inv['overrides'] or {}) else ''
            conf = (inv['confidence'] or {}).get(k)
            c = f'  [{conf:.0%}]' if isinstance(conf, (int, float)) and not mark else ''
            lines.append(f'  {k:<16} {v if v not in (None, "") else "-"}{mark}{c}')
        if ex.get('supplier_raw') and ex.get('supplier_raw') != inv.get('supplier'):
            lines.append(f"  (printed as: {ex['supplier_raw']})")
        for i in inv['issues'] or []:
            lines.append(f"  ! {i['level']}: {i['msg']}")
        if a.text:
            lines.append('---- text ----\n' + (inv.get('text') or ''))
        print('\n'.join(lines))
    finally:
        con.close()


_UPDATE_MAP = [('supplier', 'supplier'), ('number', 'invoice_number'), ('amount', 'amount'), ('currency', 'currency'),
               ('issue_date', 'issue_date'), ('fulfilment_date', 'fulfilment_date'), ('due_date', 'due_date'),
               ('payment_date', 'payment_date'), ('method', 'payment_method'), ('type', 'doc_type')]


def cmd_update(a):
    bot = _bot(a)
    changes = {field: getattr(a, arg) for arg, field in _UPDATE_MAP if getattr(a, arg) is not None}
    for f in a.clear or []:
        changes[dict(_UPDATE_MAP).get(f, f)] = None
    if a.ignore:
        changes['status'] = 'ignored'
    if a.restore:
        changes['status'] = None
    if a.not_duplicate:
        changes['not_duplicate'] = True
    if not changes:
        print('Nothing to change (see --help).')
        return 1
    try:
        inv = P.update(bot, a.id, changes, actor='cli', verify=True)
    except (ValueError, KeyError) as e:
        print(f'ERROR: {e}')
        return 1
    _out(a, P.summary(inv), _fmt_row(inv) + ''.join(f"\n  ! {i['msg']}" for i in inv['issues'] or []))


def cmd_paid(a):
    bot = _bot(a)
    for i in a.ids:
        inv = P.mark_paid(bot, i, a.date, actor='cli')
        print(_fmt_row(inv))


def cmd_unpaid(a):
    bot = _bot(a)
    for i in a.ids:
        inv = P.mark_unpaid(bot, i, actor='cli')
        print(_fmt_row(inv))


def cmd_reextract(a):
    bot = _bot(a)
    con = bot.db()
    try:
        ids = [r['id'] for r in con.execute('SELECT id FROM invoices ORDER BY id')] if a.all else a.ids
    finally:
        con.close()
    for i in ids:
        inv = P.reextract(bot, i, actor='cli')
        print(_fmt_row(inv))


# ------------------------------------------------------------------ bank
def _bank_text(res):
    lines = []
    if 'payments_in_file' in res:
        lines.append(f"{res['payments_in_file']} outgoing payments in the file, {res['new_payments']} new.")
    for m in res['matched']:
        lines.append(f"  MATCHED  invoice #{m['invoice_id']} {m['supplier']} {m['invoice_number']} "
                     f"{money(m['amount'], m['currency'])} paid {m['paid_on']} (score {m['score']})")
    for m in res['suggestions']:
        lines.append(f"  MAYBE    invoice #{m['invoice_id']} {m['supplier']} {m['invoice_number']} "
                     f"{money(m['amount'], m['currency'])} <-> payment #{m['txn_id']} on {m['paid_on']} to "
                     f"{m['counterparty'] or '?'} \"{(m['reference'] or '')[:40]}\" (score {m['score']})"
                     f"\n           confirm: invoice_bot.py bank-link {m['invoice_id']} {m['txn_id']}")
    if not res['matched'] and not res['suggestions']:
        lines.append('  No payments matched an unpaid invoice.')
    return '\n'.join(lines)


def cmd_bank(a):
    bot = _bot(a)
    res = bank.import_statement(bot, Path(a.file).read_bytes(), Path(a.file).name, a.account, actor='cli')
    _out(a, res, _bank_text(res))


def cmd_bank_match(a):
    bot = _bot(a)
    res = bank.match_all(bot, apply=True, actor='cli')
    _out(a, res, _bank_text(res))


def _bank_change(a, fn):
    bot = _bot(a)
    with bot.files_lock:
        con = bot.db()
        try:
            with P.transaction(bot, con) as journal:
                touched = fn(bot, con, journal)
            print(_fmt_row(dbm.get_invoice(con, a.invoice)))
        except (KeyError, ValueError) as e:
            print(f'ERROR: {e}')
            return 1
        finally:
            con.close()
    P._write_summaries(bot, touched)


def cmd_bank_link(a):
    return _bank_change(a, lambda bot, con, j: bank.link(bot, con, a.invoice, a.txn, None, j, actor='cli'))


def cmd_bank_unlink(a):
    return _bank_change(a, lambda bot, con, j: bank.unlink(bot, con, a.invoice, j, actor='cli'))


# ------------------------------------------------------------------ downloads
def cmd_export(a):
    bot = _bot(a)
    period = a.month or a.year
    ids = [int(x) for x in a.ids.split(',')] if a.ids else None
    if not period and not ids:
        print('Give --month YYYY-MM, --year YYYY or --ids 1,2,3')
        return 1
    res = export.export(bot, period, ids, a.include_unpaid, a.out)
    _out(a, res, f"{res['count']} invoices -> {res['path']}" +
         (f"\nMISSING files: {', '.join(res['missing'])}" if res['missing'] else ''))


# ------------------------------------------------------------------ suppliers / users
def cmd_suppliers(a):
    bot = _bot(a)
    con = bot.db()
    try:
        if a.action == 'list':
            rows = [dict(r) for r in con.execute('SELECT * FROM suppliers ORDER BY builtin, name')]
            if a.json:
                print(json.dumps(rows, ensure_ascii=False, indent=1))
                return
            for r in rows:
                if r['builtin'] and not a.all:
                    continue
                print(f"{r['name']:<28} paid_on={r['paid_on'] or '-':<15} aliases={r['aliases']} tax={r['tax_ids']} "
                      f"domains={r['domains']}")
            if not a.all:
                print('(well-known suppliers hidden; --all shows them)')
            return
        if not a.name:
            print('Give the supplier name.')
            return 1
        with con:
            if a.action == 'add':
                po = None if a.paid_on in (None, 'none') else a.paid_on
                S.upsert(con, a.name, a.alias or [], a.tax_id or [], [d.lower() for d in a.domain or []],
                         paid_on=po, set_paid_on=a.paid_on is not None)
                print(f'Saved supplier {a.name}.')
            elif a.action == 'remove':
                con.execute('DELETE FROM suppliers WHERE name = ?', (a.name,))
                print(f'Removed supplier {a.name}.')
            elif a.action == 'rename':
                con.execute('UPDATE suppliers SET name = ? WHERE name = ?', (a.new_name, a.name))
                con.execute('UPDATE invoices SET overrides = json_set(COALESCE(overrides, \'{}\'), \'$.supplier\', ?) '
                            'WHERE supplier = ?', (a.new_name, a.name))
                print(f'Renamed {a.name} -> {a.new_name}.')
    finally:
        con.close()
    if a.action in ('add', 'rename'):
        n, errors = P.refile_all(bot, "status != 'duplicate'")
        print(f'Re-checked {n} invoices.')
        for e in errors:
            print(f'  ERROR {e}')


def _read_password(a, confirm=True):
    if getattr(a, 'generate', False):
        pw = auth.generate_password()
        print(f'Generated password (shown once): {pw}')
        return pw
    if getattr(a, 'password_stdin', False):
        return sys.stdin.readline().rstrip('\n')
    pw = getpass.getpass('Password: ')
    if confirm and getpass.getpass('Again: ') != pw:
        raise ValueError('passwords do not match')
    return pw


def cmd_users(a):
    bot = _bot(a)
    con = bot.db()
    try:
        with con:
            if a.action == 'list':
                for u in auth.list_users(con):
                    print(f"{u['username']:<24} {u['role']:<7} created {u['created_at'][:10]}  last login "
                          f"{(u['last_login'] or 'never')[:16]}")
                return
            if not a.name:
                print('Give the user name.')
                return 1
            if a.action == 'add':
                auth.add_user(con, a.name, _read_password(a), a.role or 'admin')
                print(f"Added {a.role or 'admin'} {a.name}.")
            elif a.action == 'passwd':
                auth.set_password(con, a.name, _read_password(a))
                print(f'Password changed for {a.name} (logged out everywhere).')
            elif a.action == 'role':
                auth.set_role(con, a.name, a.role or 'admin')
                print(f'{a.name} is now {a.role or "admin"}.')
            elif a.action == 'remove':
                auth.remove_user(con, a.name)
                print(f'Removed {a.name}.')
    except (ValueError, KeyError) as e:
        print(f'ERROR: {e}')
        return 1
    finally:
        con.close()


# ------------------------------------------------------------------ imap
def cmd_imap(a):
    bot = _bot(a)
    if a.action == 'setup':
        icfg = dict(bot.user_config.get('imap', {}))
        icfg.update({'enabled': True, 'host': a.host or icfg.get('host', ''), 'username': a.user or icfg.get('username', '')})
        if a.port:
            icfg['port'] = a.port
        if a.folder:
            icfg['folders'] = a.folder
        if a.gmail:
            icfg['host'] = icfg['host'] or 'imap.gmail.com'
            icfg.setdefault('gmail_query', 'has:attachment')
        bot.user_config['imap'] = icfg
        bot.save_config()
        print(f"IMAP set up for {icfg['username']} at {icfg['host']}. Now store the password: "
              f'invoice_bot.py --home "{bot.home}" imap password')
    elif a.action == 'password':
        pw = sys.stdin.readline().rstrip('\n') if a.stdin else getpass.getpass('IMAP (app) password: ')
        d = bot.home / 'secrets'
        d.mkdir(exist_ok=True)
        try:
            os.chmod(d, 0o700)
        except OSError:
            pass
        p = d / 'imap_password'
        fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(pw + '\n')
        print(f'Saved to {p} (readable by you only).')
    elif a.action == 'test':
        ok, msg = collect.imap_test(bot)
        print(('OK: ' if ok else 'FAILED: ') + msg)
        return 0 if ok else 1


# ------------------------------------------------------------------ admin server / schedule
def cmd_serve(a):
    from . import web
    bot = _bot(a)
    con = bot.db()
    try:
        if not auth.list_users(con):
            print(f'No admin users yet. First run: invoice_bot.py --home "{bot.home}" users add <name>')
            return 1
    finally:
        con.close()
    web.serve(bot, a.host or bot.cfg['admin']['host'], a.port or bot.cfg['admin']['port'],
              collect_every=a.collect_every if a.collect_every is not None else bot.cfg['admin']['collect_every_minutes'])


def cmd_schedule(a):
    bot = _bot(a)
    py = sys.executable
    script = str(Path(sys.argv[0]).resolve())
    home = str(bot.home)
    every = max(5, a.every)
    serve_flag = f' --collect-every {every}' if a.serve else ''
    print('# --- cron (Linux / macOS): crontab -e, then add:')
    print(f'*/{every} * * * * "{py}" "{script}" --home "{home}" run >> "{home}/logs/cron.log" 2>&1')
    if a.serve:
        print(f'@reboot "{py}" "{script}" --home "{home}" serve{serve_flag} >> "{home}/logs/serve.log" 2>&1')
    print('\n# --- macOS launchd: save as ~/Library/LaunchAgents/hu.invoicebot.run.plist, then\n'
          '#     launchctl load ~/Library/LaunchAgents/hu.invoicebot.run.plist')
    args = ''.join(f'<string>{x}</string>' for x in [py, script, '--home', home] + (['serve', '--collect-every', str(every)] if a.serve else ['run']))
    keep = '<key>KeepAlive</key><true/>' if a.serve else f'<key>StartInterval</key><integer>{every * 60}</integer>'
    print(f'<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" '
          f'"http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n<plist version="1.0"><dict>'
          f'<key>Label</key><string>hu.invoicebot.run</string><key>ProgramArguments</key><array>{args}</array>'
          f'{keep}<key>RunAtLoad</key><true/><key>StandardOutPath</key><string>{home}/logs/launchd.log</string>'
          f'<key>StandardErrorPath</key><string>{home}/logs/launchd.log</string></dict></plist>')
    print('\n# --- systemd (Linux server): ~/.config/systemd/user/invoicebot.service, then\n'
          '#     systemctl --user enable --now invoicebot')
    print(f'[Unit]\nDescription=Invoice bot\n\n[Service]\nExecStart="{py}" "{script}" --home "{home}" serve '
          f'--collect-every {every}\nRestart=on-failure\n\n[Install]\nWantedBy=default.target')
    print('\n# --- Windows Task Scheduler (run in cmd):')
    print(f'schtasks /Create /SC MINUTE /MO {every} /TN "InvoiceBot" /TR "\\"{py}\\" \\"{script}\\" --home \\"{home}\\" run"')


# ------------------------------------------------------------------ maintenance
def cmd_verify(a):
    bot = _bot(a)
    if a.fix:
        adopted, n, errors = P.repair(bot)
        print(f'Re-attached {adopted} file(s) found elsewhere in the archive; re-filed {n} invoices.')
        for e in errors:
            print(f'  ERROR {e}')
    problems = P.find_problems(bot)
    for kind, inv_id, path in problems:
        if kind == 'missing':
            print(f'#{inv_id}: file missing: {path}' + ('' if a.fix else '  (verify --fix looks for it)'))
        else:
            print(f'not in the ledger: {path} (drop it into the inbox to add it)')
    if not problems:
        print('Archive and ledger agree.')
    return 1 if problems else 0


def cmd_demo(a):
    from . import samples
    home = Path(a.home).expanduser() if a.home else Path.home() / 'InvoiceBot-demo'
    if (home / 'invoicebot.json').exists() and not a.force:
        print(f'{home} already exists (use --force to add the demo invoices again).')
        return 1
    bot = Bot(home, create=True)
    bot.user_config.update({'company': samples.DEMO_COMPANY})
    bot.save_config()
    bot = Bot(home)
    con = bot.db()
    try:
        with con:
            S.seed_builtin(con)
    finally:
        con.close()
    for name, data in samples.demo_files():
        (bot.inbox / name).write_bytes(data)
        os.utime(bot.inbox / name, (0, 0))
    print(f'Demo home: {bot.home}\n--- collecting the sample invoices from the inbox ---')
    rep = collect.run(bot, imap=False)
    print(rep.text())
    huf, eur = samples.demo_bank_csv()
    print('\n--- importing two bank statements (confirms when the transfer invoices were paid) ---')
    for name, data in (('otp_2026-09.csv', huf), ('wise_eur.csv', eur)):
        res = bank.import_statement(bot, data, name, actor='demo')
        print(_bank_text(res))
    print('\n--- the archive ---')
    for p in sorted(bot.archive.rglob('*')):
        if p.is_file():
            print('  ' + str(p.relative_to(bot.archive)))
    print(f'\nNext: invoice_bot.py --home "{bot.home}" users add admin   then   ... serve   and open '
          f'http://127.0.0.1:{bot.cfg["admin"]["port"]}')


# ------------------------------------------------------------------ parser
def build_parser():
    ap = argparse.ArgumentParser(prog='invoice_bot.py', description='Automated invoice bot: collect, identify, '
                                 'rename and organise invoices by payment month.')
    ap.add_argument('--home', help='bot folder (default: $INVOICEBOT_HOME or ~/InvoiceBot)')
    ap.add_argument('--version', action='version', version=__version__)
    sub = ap.add_subparsers(dest='cmd', required=True)

    p = sub.add_parser('init', help='set up a bot folder / change company details')
    p.add_argument('--company')
    p.add_argument('--alias', action='append', help='other names of your company')
    p.add_argument('--tax-id', action='append', help='your tax numbers (12345678-2-42, HU12345678)')
    p.add_argument('--domain', action='append', help="your e-mail domain(s), e.g. example.hu")
    p.add_argument('--currency', help='default currency (HUF)')
    p.add_argument('--archive', help='archive folder (e.g. a shared Google Drive folder)')
    p.add_argument('--csv-locale', choices=['hu', 'eu', 'en'], help='CSV format: hu/eu = ; and decimal comma')
    p.add_argument('--force', action='store_true')
    p.set_defaults(fn=cmd_init)

    p = sub.add_parser('config', help='show or change a setting: config payment.unconfirmed estimate')
    p.add_argument('key', nargs='?')
    p.add_argument('value', nargs='?')
    p.set_defaults(fn=cmd_config)

    p = sub.add_parser('check', help='check tools, folders and the mailbox connection')
    p.set_defaults(fn=cmd_check)

    p = sub.add_parser('status', help='overview: what is filed, unpaid, waiting for review')
    p.add_argument('--json', action='store_true')
    p.set_defaults(fn=cmd_status)

    p = sub.add_parser('run', help='collect new invoices now (inbox folder + mailbox)')
    p.add_argument('--no-imap', action='store_true')
    p.add_argument('--no-inbox', action='store_true')
    p.add_argument('--json', action='store_true')
    p.set_defaults(fn=cmd_run)

    p = sub.add_parser('add', help='add invoice files (PDF, image, .eml, .zip)')
    p.add_argument('files', nargs='+')
    p.add_argument('--sender', help='e-mail sender, helps identify the supplier: "Name <a@b.com>"')
    p.add_argument('--subject')
    p.add_argument('--source', default='cli')
    p.add_argument('--json', action='store_true')
    p.set_defaults(fn=cmd_add)

    p = sub.add_parser('list', help='list invoices')
    p.add_argument('--month', help='YYYY-MM (payment month)')
    p.add_argument('--year')
    p.add_argument('--status', choices=['all', 'filed', 'paid', 'unpaid', 'review', 'duplicate', 'ignored'])
    p.add_argument('--supplier')
    p.add_argument('--search')
    p.add_argument('--limit', type=int)
    p.add_argument('--json', action='store_true')
    p.set_defaults(fn=cmd_list)

    p = sub.add_parser('show', help='one invoice in detail')
    p.add_argument('id', type=int)
    p.add_argument('--text', action='store_true', help='include the extracted text')
    p.add_argument('--json', action='store_true')
    p.set_defaults(fn=cmd_show)

    p = sub.add_parser('update', help='correct fields (the file is renamed / moved to match)')
    p.add_argument('id', type=int)
    for arg, _ in _UPDATE_MAP:
        p.add_argument('--' + arg.replace('_', '-'), dest=arg)
    p.add_argument('--clear', action='append', help='drop a manual value, back to what was read from the invoice')
    p.add_argument('--ignore', action='store_true', help='not an invoice: move to other documents')
    p.add_argument('--restore', action='store_true', help='undo --ignore')
    p.add_argument('--not-duplicate', action='store_true')
    p.add_argument('--json', action='store_true')
    p.set_defaults(fn=cmd_update)

    p = sub.add_parser('paid', help='mark invoices paid (moves them into the payment month)')
    p.add_argument('ids', type=int, nargs='+')
    p.add_argument('--date', help='payment date YYYY-MM-DD (default today)')
    p.set_defaults(fn=cmd_paid)

    p = sub.add_parser('unpaid', help='mark invoices as not paid')
    p.add_argument('ids', type=int, nargs='+')
    p.set_defaults(fn=cmd_unpaid)

    p = sub.add_parser('reextract', help='read invoices again with the current rules')
    p.add_argument('ids', type=int, nargs='*')
    p.add_argument('--all', action='store_true')
    p.set_defaults(fn=cmd_reextract)

    p = sub.add_parser('bank', help='import a bank statement CSV and confirm payment dates')
    p.add_argument('file')
    p.add_argument('--account', help='a name for the account (if you import several)')
    p.add_argument('--json', action='store_true')
    p.set_defaults(fn=cmd_bank)

    p = sub.add_parser('bank-match', help='match imported payments to invoices again')
    p.add_argument('--json', action='store_true')
    p.set_defaults(fn=cmd_bank_match)

    p = sub.add_parser('bank-link', help='confirm a suggested match: bank-link INVOICE_ID PAYMENT_ID')
    p.add_argument('invoice', type=int)
    p.add_argument('txn', type=int)
    p.set_defaults(fn=cmd_bank_link)

    p = sub.add_parser('bank-unlink', help='undo a bank match')
    p.add_argument('invoice', type=int)
    p.set_defaults(fn=cmd_bank_unlink)

    p = sub.add_parser('export', help='ZIP of invoices + CSV summary for a month / year / selection')
    p.add_argument('--month')
    p.add_argument('--year')
    p.add_argument('--ids')
    p.add_argument('--include-unpaid', action='store_true', help='also unpaid invoices expected in the period')
    p.add_argument('--out')
    p.add_argument('--json', action='store_true')
    p.set_defaults(fn=cmd_export)

    p = sub.add_parser('suppliers', help='list / add / remove / rename suppliers and their payment rules')
    p.add_argument('action', choices=['list', 'add', 'remove', 'rename'])
    p.add_argument('name', nargs='?')
    p.add_argument('new_name', nargs='?')
    p.add_argument('--alias', action='append', help='name as printed on invoices')
    p.add_argument('--tax-id', action='append')
    p.add_argument('--domain', action='append', help='sender e-mail domain')
    p.add_argument('--paid-on', choices=['issue_date', 'due_date', 'fulfilment_date', 'none'],
                   help='auto-charged supplier: invoices count as paid on this date')
    p.add_argument('--all', action='store_true')
    p.add_argument('--json', action='store_true')
    p.set_defaults(fn=cmd_suppliers)

    p = sub.add_parser('users', help='admin logins for the web panel')
    p.add_argument('action', choices=['list', 'add', 'passwd', 'role', 'remove'])
    p.add_argument('name', nargs='?')
    p.add_argument('--role', choices=list(auth.ROLES))
    g = p.add_mutually_exclusive_group()
    g.add_argument('--password-stdin', action='store_true')
    g.add_argument('--generate', action='store_true', help='generate a password and print it once')
    p.set_defaults(fn=cmd_users)

    p = sub.add_parser('imap', help='mailbox: setup / password / test')
    p.add_argument('action', choices=['setup', 'password', 'test'])
    p.add_argument('--host')
    p.add_argument('--user')
    p.add_argument('--port', type=int)
    p.add_argument('--folder', action='append')
    p.add_argument('--gmail', action='store_true')
    p.add_argument('--stdin', action='store_true')
    p.set_defaults(fn=cmd_imap)

    p = sub.add_parser('serve', help='start the admin web panel')
    p.add_argument('--host')
    p.add_argument('--port', type=int)
    p.add_argument('--collect-every', type=int, help='also collect every N minutes')
    p.set_defaults(fn=cmd_serve)

    p = sub.add_parser('schedule', help='print cron / launchd / systemd / Task Scheduler setups')
    p.add_argument('--every', type=int, default=30, help='minutes between runs')
    p.add_argument('--serve', action='store_true', help='keep the admin panel running and collect from it')
    p.set_defaults(fn=cmd_schedule)

    p = sub.add_parser('verify', help='check that the archive and the ledger agree')
    p.add_argument('--fix', action='store_true', help='re-file every invoice where it belongs')
    p.set_defaults(fn=cmd_verify)

    p = sub.add_parser('demo', help='create a demo bot with sample invoices')
    p.add_argument('--force', action='store_true')
    p.set_defaults(fn=cmd_demo)
    return ap


def main(argv=None):
    a = build_parser().parse_args(argv)
    try:
        rc = a.fn(a)
    except FileNotFoundError as e:
        print(f'ERROR: {e}', file=sys.stderr)
        rc = 2
    except KeyboardInterrupt:
        rc = 130
    except BrokenPipeError:  # output piped into head & co.
        try:
            sys.stdout = open(os.devnull, 'w')
        except OSError:
            pass
        rc = 0
    sys.exit(rc or 0)
