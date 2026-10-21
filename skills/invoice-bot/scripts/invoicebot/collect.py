"""Collect invoices automatically: the inbox drop folder and an IMAP mailbox.

- inbox/: every PDF, image, .eml (saved e-mail) or .zip dropped here is processed and removed. Point a
  scanner app, an e-mail-to-folder rule or a synced cloud folder at it.
- IMAP: new messages in the configured folders are checked for PDF attachments (also inside forwarded
  e-mails and ZIP files). Nothing is deleted or moved in the mailbox; processed messages are remembered
  in the ledger, optionally marked as read or labelled (Gmail).
"""
import base64
import email
import email.policy
import imaplib
import io
import os
import re
import socket
import ssl
import time
import zipfile
import zlib
from datetime import timedelta
from email.utils import parseaddr
from pathlib import Path, PurePosixPath

from . import db as dbm
from . import pipeline as P
from . import textract
from .util import now_iso, today

SKIP_NAMES = re.compile(r'^(?:\.|~\$)|\.(?:part|crdownload|tmp|download|icloud)$|^(?:thumbs\.db|desktop\.ini)$', re.I)
_IMAP_MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


class Report:
    def __init__(self):
        self.items = []
        self.errors = []
        self.sources = {}
        self.touched = set()
        self.started = now_iso()

    def add(self, source, res):
        res = dict(res)
        res['source'] = source
        self.items.append(res)
        self.sources[source] = self.sources.get(source, 0) + 1

    def error(self, where, err):
        self.errors.append({'where': where, 'error': str(err)})

    def counts(self):
        c = {'new': 0, 'filed': 0, 'unpaid': 0, 'review': 0, 'duplicate': 0, 'ignored': 0, 'skipped': 0,
             'already_known': 0}
        for it in self.items:
            r = it['result']
            if r == 'new':
                c['new'] += 1
                st = it.get('status')
                if st == 'filed':
                    c['filed' if it.get('paid') else 'unpaid'] += 1
                elif st in c:
                    c[st] += 1
            elif r == 'duplicate_file':
                c['already_known'] += 1
            elif r == 'skipped':
                c['skipped'] += 1
        return c

    def as_dict(self):
        return {'started': self.started, 'finished': now_iso(), 'counts': self.counts(), 'items': self.items,
                'errors': self.errors}

    def text(self):
        c = self.counts()
        lines = [f"New invoices: {c['new']}  (filed {c['filed']}, waiting for payment {c['unpaid']}, "
                 f"need review {c['review']}, duplicates {c['duplicate']}, other documents {c['ignored']})"]
        if c['already_known'] or c['skipped']:
            lines.append(f"Already in the archive: {c['already_known']}   not invoices / skipped: {c['skipped']}")
        for it in self.items:
            if it['result'] != 'new':
                continue
            tag = {'filed': 'PAID' if it.get('paid') else 'UNPAID', 'review': 'REVIEW', 'duplicate': 'DUPLICATE',
                   'ignored': 'OTHER'}.get(it.get('status'), it.get('status', '').upper())
            lines.append(f"  #{it['id']:<5} {tag:<9} {it.get('file_path')}")
            for msg in it.get('issues') or []:
                lines.append(f'         - {msg}')
        for e in self.errors:
            lines.append(f"ERROR {e['where']}: {e['error']}")
        return '\n'.join(lines)


# ------------------------------------------------------------------ containers
MAX_FILES_PER_ITEM = 100     # files taken out of one e-mail (anyone can send mail), all levels together
MAX_FILES_PER_DROP = 2000    # files taken out of one file an admin dropped or uploaded
_ZIP_ERRORS = (zipfile.BadZipFile, zipfile.LargeZipFile, RuntimeError, NotImplementedError, OSError, ValueError,
               EOFError, zlib.error)


class Outcome:
    """What became of one file and everything inside it."""

    def __init__(self):
        self.handled = self.skipped = self.unreadable = self.failed = 0
        self.notes = []

    def merge(self, other):
        self.handled += other.handled
        self.skipped += other.skipped
        self.unreadable += other.unreadable
        self.failed += other.failed
        self.notes += other.notes
        return self

    @property
    def complete(self):
        """Everything in it was imported (or was already in the archive)."""
        return self.handled > 0 and not (self.skipped or self.unreadable or self.failed)


def iter_mail_parts(msg):
    """(filename, bytes, decoration) for every attachment, including inside attached / forwarded messages.
    decoration is True for inline images such as logos and signatures."""
    for part in msg.walk():
        if part.is_multipart():
            continue
        ctype = part.get_content_type()
        if ctype == 'message/rfc822':
            continue
        fname = part.get_filename() or ''
        disp = (part.get_content_disposition() or '').lower()
        if not fname and disp != 'attachment' and ctype != 'application/pdf':
            continue
        try:
            data = part.get_payload(decode=True)
        except Exception:
            data = None
        if not data:
            continue
        decoration = ctype.startswith('image/') and (disp == 'inline' or bool(part.get('Content-ID')))
        yield fname or ('attachment.pdf' if ctype == 'application/pdf' else 'attachment'), data, decoration


def iter_zip(data, max_total=200 * 1024 * 1024):
    """(name, bytes, problem) for every member; bytes is None and problem says why when it was not read."""
    try:
        zf = zipfile.ZipFile(io.BytesIO(data))
        infos = zf.infolist()
    except _ZIP_ERRORS as e:
        yield None, None, f'unreadable ZIP ({e})'
        return
    total = 0
    for info in infos:
        if info.is_dir():
            continue
        name = PurePosixPath(info.filename.replace('\\', '/')).name or 'file'
        if info.file_size > 50 * 1024 * 1024:
            yield name, None, 'larger than 50 MB'
            continue
        total += info.file_size
        if total > max_total:
            yield name, None, 'the ZIP holds more than 200 MB'
            continue
        try:
            with zf.open(info) as f:
                blob = f.read(50 * 1024 * 1024 + 1)
        except _ZIP_ERRORS as e:  # encrypted, unsupported compression, bad CRC
            yield name, None, f'cannot be read ({e})'
            continue
        yield name, blob, None


def mail_meta(msg):
    return {'sender': str(msg.get('From', '')), 'subject': str(msg.get('Subject', '')),
            'message_id': str(msg.get('Message-ID', '')).strip(), 'date': str(msg.get('Date', ''))}


def process_blob(bot, data, name, source, meta, report, require_invoice, depth=0, budget=None, in_zip=False):
    """A file of any supported kind: pdf/image -> ingest; eml/zip -> their contents. Returns an Outcome."""
    out = Outcome()
    if budget is None:
        budget = {'left': MAX_FILES_PER_ITEM if source == 'imap' else MAX_FILES_PER_DROP}
    max_bytes = bot.cfg['collect'].get('max_attachment_mb', 25) * 1024 * 1024
    if len(data) > max_bytes:
        out.skipped += 1
        out.notes.append(f'{name}: larger than {max_bytes // 1048576} MB')
        report.add(source, {'result': 'skipped', 'name': name, 'reason': f'larger than {max_bytes // 1048576} MB'})
        return out
    kind = textract.sniff(data, name)
    try:
        if kind == 'eml':
            if depth >= 3:
                out.skipped += 1
                out.notes.append(f'{name}: e-mails nested too deep')
                return out
            msg = email.message_from_bytes(data, policy=email.policy.default)
            m = dict(meta or {})
            m.update({k: v for k, v in mail_meta(msg).items() if v})
            for fname, blob, decoration in iter_mail_parts(msg):
                if decoration:
                    continue
                out.merge(process_blob(bot, blob, fname, source, m, report, require_invoice, depth + 1, budget, in_zip))
            return out
        if kind == 'zip':
            if in_zip or depth >= 3:
                out.skipped += 1
                out.notes.append(f'{name}: a ZIP inside a ZIP is not opened')
                report.add(source, {'result': 'skipped', 'name': name, 'reason': 'a ZIP inside a ZIP is not opened'})
                return out
            for fname, blob, problem in iter_zip(data):
                if problem:
                    out.unreadable += 1
                    out.notes.append(f'{fname or name}: {problem}')
                    report.add(source, {'result': 'skipped', 'name': f'{name}/{fname}' if fname else name,
                                        'reason': problem})
                    continue
                out.merge(process_blob(bot, blob, fname, source, meta, report, require_invoice, depth + 1, budget,
                                       in_zip=True))
            return out
    except Exception as e:  # a broken container must not stop the run
        bot.log.exception('cannot open %s', name)
        out.unreadable += 1
        out.notes.append(f'{name}: cannot be opened ({e})')
        report.add(source, {'result': 'skipped', 'name': name, 'reason': f'cannot be opened ({e})'})
        return out
    if kind is None:
        out.skipped += 1
        out.notes.append(f'{name}: not a PDF, image, e-mail or ZIP')
        if depth == 0:
            report.add(source, {'result': 'skipped', 'name': name, 'reason': 'not a PDF, image, e-mail or ZIP'})
        return out
    if kind == 'image' and depth > 0 and not bot.cfg['collect'].get('include_images'):
        out.skipped += 1
        out.notes.append(f'{name}: an image (collect.include_images is off)')
        return out
    if budget['left'] <= 0:
        out.skipped += 1
        out.notes.append(f'{name}: too many files in one item')
        return out
    budget['left'] -= 1
    try:
        res = P.ingest(bot, data, name, source, meta, require_invoice=require_invoice, touched=report.touched)
    except Exception as e:  # e.g. the archive is not writable: try again next run
        bot.log.exception('ingest failed for %s', name)
        report.error(name, e)
        out.failed += 1
        out.notes.append(f'{name}: {e}')
        return out
    report.add(source, res)
    bot.log.info('%s %s -> %s', source, name, res.get('file_path') or res.get('reason') or res['result'])
    if res['result'] in ('new', 'duplicate_file'):
        out.handled += 1
    else:
        out.skipped += 1
        out.notes.append(f"{name}: {res.get('reason')}")
    return out


# ------------------------------------------------------------------ inbox folder
NOT_PROCESSED = '_not_processed'


def free_name(path):
    """path, or path_2 / path_3 ... when it is taken."""
    if not path.exists():
        return path
    for k in range(2, 100000):
        cand = path.with_name(f'{path.stem}_{k}{path.suffix}')
        if not cand.exists():
            return cand
    raise OSError(f'no free name for {path}')


def collect_inbox(bot, report, settle_seconds=5):
    """Process everything in the inbox folder. A file is removed only when everything in it was imported;
    a file that held nothing (or not only) invoices moves to inbox/_not_processed/ (never deleted, never
    overwritten); a file that failed for a passing reason stays for the next run."""
    root = bot.inbox
    for path in sorted(p for p in root.rglob('*') if p.is_file()):
        rel_parts = path.relative_to(root).parts
        if SKIP_NAMES.search(path.name) or any(SKIP_NAMES.search(p) or p.startswith('_') for p in rel_parts[:-1]):
            continue
        try:
            if time.time() - path.stat().st_mtime < settle_seconds:
                continue  # still being written / synced
            data = path.read_bytes()
        except OSError as e:
            report.error(str(path), e)
            continue
        out = process_blob(bot, data, path.name, 'inbox', {'path': str(path.relative_to(root))}, report,
                           require_invoice=False)
        if out.failed:
            continue
        try:
            if out.complete:
                path.unlink()
                continue
            dest = free_name(root / NOT_PROCESSED / path.name)
            dest.parent.mkdir(exist_ok=True)
            path.replace(dest)
            if out.handled:
                why = f'{out.handled} invoice(s) imported, the rest not: ' + '; '.join(out.notes[:5])
            else:
                why = 'no invoice found' + (': ' + '; '.join(out.notes[:3]) if out.notes else '')
            report.add('inbox', {'result': 'skipped', 'name': path.name,
                                 'reason': f'{why}. Moved to inbox/{NOT_PROCESSED}/{dest.name}'})
        except OSError as e:
            report.error(str(path), e)
    for d in sorted((p for p in root.rglob('*') if p.is_dir()), key=lambda p: -len(p.parts)):
        if d.name == NOT_PROCESSED:
            continue
        try:
            d.rmdir()
        except OSError:
            pass


# ------------------------------------------------------------------ IMAP
def imap_utf7(name):
    """Folder names are sent in IMAP's modified UTF-7 ("Számlák" -> "Sz&AOE-ml&AOE-k")."""
    out, buf = [], []

    def flush():
        if buf:
            b = base64.b64encode(''.join(buf).encode('utf-16-be')).decode('ascii').rstrip('=').replace('/', ',')
            out.append('&' + b + '-')
            buf.clear()

    for c in name:
        if 0x20 <= ord(c) <= 0x7e:
            flush()
            out.append('&-' if c == '&' else c)
        else:
            buf.append(c)
    flush()
    return ''.join(out)


def _quote(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def imap_password(icfg, home):
    env = icfg.get('password_env') or 'INVOICEBOT_IMAP_PASSWORD'
    if os.environ.get(env):
        return os.environ[env]
    pf = icfg.get('password_file')
    for p in ([Path(pf).expanduser()] if pf else []) + [Path(home) / 'secrets' / 'imap_password']:
        if not p.is_absolute():
            p = Path(home) / p
        if p.exists():
            return p.read_text(encoding='utf-8').strip()
    raise RuntimeError(f'IMAP password not set: put it in the {env} environment variable or run '
                       f'"invoice_bot.py imap password".')


def imap_connect(icfg, password, timeout=60):
    host, port = icfg['host'], int(icfg.get('port') or 993)
    ctx = ssl.create_default_context()
    if icfg.get('ssl', True):
        M = imaplib.IMAP4_SSL(host, port, ssl_context=ctx, timeout=timeout)
    else:
        M = imaplib.IMAP4(host, port, timeout=timeout)
        M.starttls(ssl_context=ctx)
    M.login(icfg['username'], password)
    return M


def _fetch_parts(data):
    """Group an imaplib FETCH response into one bytes blob per message."""
    msgs, cur = [], b''
    for part in data or []:
        if isinstance(part, tuple):
            head, lit = part[0], part[1]
            if re.match(rb'^\d+ \(', head) and cur:
                msgs.append(cur)
                cur = b''
            cur += head + lit
        elif isinstance(part, bytes):
            if re.match(rb'^\d+ \(', part) and cur:
                msgs.append(cur)
                cur = b''
            cur += part
    if cur:
        msgs.append(cur)
    return msgs


def _allowed_sender(icfg, sender):
    addr = parseaddr(sender or '')[1].lower()
    only = [s.lower() for s in icfg.get('only_from') or []]
    ignore = [s.lower() for s in icfg.get('ignore_from') or []]
    if any(addr == s or addr.endswith('@' + s.lstrip('@')) or addr.endswith('.' + s.lstrip('@')) for s in ignore):
        return False
    if only:
        return any(addr == s or addr.endswith('@' + s.lstrip('@')) or addr.endswith('.' + s.lstrip('@')) for s in only)
    return True


MAX_TRIES = 3  # a message whose processing failed is tried again on this many runs


def _tries_left(row):
    """None when the message is done; else how many earlier attempts failed."""
    if row is None:
        return 0
    m = re.match(r'retry:(\d+)', row['result'] or '')
    return int(m.group(1)) if m else None


def _search(M, icfg, since):
    if icfg.get('gmail_query'):
        q = icfg['gmail_query'] + f' after:{since:%Y/%m/%d}'
        if q.isascii():
            return M.uid('SEARCH', 'X-GM-RAW', _quote(q))
        M.literal = q.encode('utf-8')  # e.g. "subject:számla": sent as a UTF-8 literal
        return M.uid('SEARCH', 'CHARSET', 'UTF-8', 'X-GM-RAW')
    crit = ['SINCE', f'{since.day:02d}-{_IMAP_MONTHS[since.month - 1]}-{since.year}']
    if icfg.get('search'):
        if not icfg['search'].isascii():
            raise ValueError('imap.search must be plain ASCII; use imap.only_from, or gmail_query on Gmail')
        crit = ['(' + icfg['search'] + ')'] + crit
    return M.uid('SEARCH', None, *crit)


def _leave_folder(M):
    """Leave the folder without CLOSE, which would expunge messages another client flagged as deleted."""
    try:
        if 'UNSELECT' in getattr(M, 'capabilities', ()):
            M.unselect()
    except imaplib.IMAP4.error:
        pass


def collect_imap(bot, report, connect=imap_connect):
    icfg = bot.cfg['imap']
    if not icfg.get('enabled'):
        return
    account = f"{icfg['username']}@{icfg['host']}"
    try:
        M = connect(icfg, imap_password(icfg, bot.home))
    except (imaplib.IMAP4.error, OSError, socket.error, RuntimeError, ssl.SSLError) as e:
        report.error(f'imap {account}', f'cannot log in: {e}')
        return
    con = bot.db()
    try:
        since = today() - timedelta(days=int(icfg.get('lookback_days') or 45))
        writable = bool(icfg.get('mark_seen') or icfg.get('gmail_label'))
        for folder in icfg.get('folders') or ['INBOX']:
            try:
                typ, _ = M.select(_quote(imap_utf7(folder)), readonly=not writable)
                if typ != 'OK':
                    report.error(f'imap {folder}', 'cannot open folder')
                    continue
                uidv = (M.response('UIDVALIDITY')[1] or [b'0'])[0]
                uidv = uidv.decode() if isinstance(uidv, bytes) else str(uidv)
                typ, data = _search(M, icfg, since)
                if typ != 'OK':
                    report.error(f'imap {folder}', 'search failed')
                    continue
                uids = [u for u in (data[0] or b'').split() if u]
                prefix = f'imap:{account}/{folder}/{uidv}/'
                todo = []
                for u in uids:
                    tries = _tries_left(con.execute('SELECT result FROM seen_messages WHERE key = ?',
                                                    (prefix + u.decode(),)).fetchone())
                    if tries is not None:
                        todo.append((u, tries))
                for i in range(0, len(todo), 100):
                    batch = todo[i:i + 100]
                    typ, data = M.uid('FETCH', b','.join(u for u, _ in batch),
                                      '(UID BODYSTRUCTURE BODY.PEEK[HEADER.FIELDS (FROM MESSAGE-ID)])')
                    if typ != 'OK':  # nothing is recorded: the whole batch is tried again next run
                        report.error(f'imap {folder}', f'fetching message structure failed: {data}')
                        continue
                    has_files = {}
                    for blob in _fetch_parts(data):
                        m = re.search(rb'UID (\d+)', blob)
                        if m:
                            low = blob.lower()
                            has_files[m.group(1)] = (b'pdf' in low or b'"zip"' in low or b'.zip' in low
                                                     or b'rfc822' in low or b'octet-stream' in low
                                                     or (bot.cfg['collect'].get('include_images') and b'image' in low),
                                                     blob)
                    for uid, tries in batch:
                        if uid not in has_files:  # the server did not return it this time
                            continue
                        _one_message(bot, con, M, icfg, report, account, folder, prefix, uid, tries, has_files[uid])
            except ValueError as e:
                report.error(f'imap {folder}', e)
            finally:
                _leave_folder(M)
    except (imaplib.IMAP4.error, OSError, socket.error, ssl.SSLError) as e:
        report.error(f'imap {account}', e)
    finally:
        con.close()
        try:
            M.logout()
        except Exception:
            pass


def _one_message(bot, con, M, icfg, report, account, folder, prefix, uid, tries, fetched):
    key = prefix + uid.decode()
    candidate, head = fetched
    msg_id = re.search(rb'message-id:\s*(<[^>]+>)', head, re.I)
    mid_key = 'msgid:' + msg_id.group(1).decode('utf-8', 'ignore') if msg_id else None
    if mid_key and _tries_left(con.execute('SELECT result FROM seen_messages WHERE key = ?',
                                           (mid_key,)).fetchone()) is None:
        candidate = False  # the same message, already handled in another folder
    result, retry = 'no attachment', False
    if candidate:
        try:
            typ, data = M.uid('FETCH', uid, '(BODY.PEEK[])')
            raw = next((p[1] for p in data or [] if isinstance(p, tuple)), None) if typ == 'OK' else None
            if raw is None:
                result, retry = 'could not be fetched', True
            else:
                msg = email.message_from_bytes(raw, policy=email.policy.default)
                meta = mail_meta(msg)
                meta['mailbox'] = f'{account}/{folder}'
                if not _allowed_sender(icfg, meta['sender']):
                    result = 'sender filtered'
                else:
                    out, budget = Outcome(), {'left': MAX_FILES_PER_ITEM}
                    n0 = len(report.items)
                    for fname, blob, decoration in iter_mail_parts(msg):
                        if not decoration:
                            out.merge(process_blob(bot, blob, fname, 'imap', meta, report, require_invoice=True,
                                                   depth=1, budget=budget))
                    got = [it for it in report.items[n0:] if it['result'] == 'new']
                    result = f'{len(got)} invoice(s)' if got else 'no invoice'
                    if out.failed:
                        result, retry = f'{len(got)} invoice(s); {out.failed} failed: ' + '; '.join(out.notes[:3]), True
                    if got:
                        _after_processed(M, uid, icfg)
        except (imaplib.IMAP4.error, OSError, ssl.SSLError):
            raise  # the connection is gone: stop this run, nothing recorded for this message
        except Exception as e:  # anything else about this one message: record it and go on
            bot.log.exception('imap message %s in %s failed', uid, folder)
            report.error(f'imap {folder} message {uid.decode()}', e)
            result, retry = f'error: {e}', True
    if retry:
        tries += 1
        result = f'retry:{tries} {result}' if tries < MAX_TRIES else f'gave up after {tries} attempts: {result}'
    with con:
        con.execute('INSERT OR REPLACE INTO seen_messages(key, at, result) VALUES (?, ?, ?)', (key, now_iso(), result))
        if mid_key and not result.startswith('retry:'):
            con.execute('INSERT OR REPLACE INTO seen_messages(key, at, result) VALUES (?, ?, ?)',
                        (mid_key, now_iso(), result))


def _after_processed(M, uid, icfg):
    try:
        if icfg.get('mark_seen'):
            M.uid('STORE', uid, '+FLAGS', '(\\Seen)')
        if icfg.get('gmail_label'):
            M.uid('STORE', uid, '+X-GM-LABELS', '(' + _quote(imap_utf7(icfg['gmail_label'])) + ')')
    except imaplib.IMAP4.error:
        pass


def imap_test(bot):
    """Log in and list folders: returns (ok, message)."""
    icfg = bot.cfg['imap']
    try:
        M = imap_connect(icfg, imap_password(icfg, bot.home), timeout=30)
    except Exception as e:
        return False, f'login failed: {e}'
    try:
        typ, folders = M.list()
        names = []
        for f in folders or []:
            s = f.decode('utf-8', 'ignore') if isinstance(f, bytes) else str(f)
            m = re.search(r'"([^"]*)"\s*$|(\S+)\s*$', s)
            if m:
                names.append(m.group(1) or m.group(2))
        return True, 'logged in; folders: ' + ', '.join(names[:40])
    finally:
        try:
            M.logout()
        except Exception:
            pass


# ------------------------------------------------------------------ one run
def run(bot, inbox=True, imap=True, actor='bot'):
    """Collect from all sources. Returns the report, or None if another run is in progress."""
    if not bot.run_lock.acquire(blocking=False):
        return None
    try:
        report = Report()
        if inbox:
            try:
                collect_inbox(bot, report)
            except Exception as e:
                bot.log.exception('inbox collection failed')
                report.error('inbox', e)
        if imap:
            try:
                collect_imap(bot, report)
            except Exception as e:
                bot.log.exception('imap collection failed')
                report.error('imap', e)
        P._write_summaries(bot, report.touched)
        con = bot.db()
        try:
            with con:
                dbm.meta_set(con, 'last_run', report.as_dict())
                c = report.counts()
                if c['new'] or report.errors:
                    dbm.log_event(con, 'collected', None, actor, {'counts': c, 'errors': len(report.errors)})
        finally:
            con.close()
        bot.log.info('run finished: %s', report.counts())
        return report
    finally:
        bot.run_lock.release()
