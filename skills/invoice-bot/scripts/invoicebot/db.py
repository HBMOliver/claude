"""The ledger: one SQLite file holding every invoice, supplier, admin user, bank payment and event."""
import sqlite3

from .util import jdump, jload, now_iso

SCHEMA_VERSION = 1

SCHEMA = """
CREATE TABLE IF NOT EXISTS invoices (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    sha256          TEXT NOT NULL UNIQUE,
    file_path       TEXT NOT NULL,          -- relative to the archive folder, '/' separators
    original_name   TEXT,
    source          TEXT,                   -- imap / inbox / upload / cli
    source_detail   TEXT,                   -- JSON: sender, subject, message id, mailbox
    received_at     TEXT,
    doc_type        TEXT,                   -- invoice / receipt / credit_note / proforma / unknown
    supplier        TEXT,
    supplier_raw    TEXT,
    supplier_tax_id TEXT,
    invoice_number  TEXT,
    issue_date      TEXT,
    fulfilment_date TEXT,
    due_date        TEXT,
    payment_method  TEXT,
    amount          TEXT,                   -- decimal string, e.g. '127000.00'
    currency        TEXT,
    payment_date    TEXT,                   -- confirmed payment date, or the expected one when paid=0
    payment_source  TEXT,                   -- manual / bank / invoice / supplier_rule / payment_method /
                                            -- paid_stamp / direct_debit / expected_due / expected_issue
    paid            INTEGER NOT NULL DEFAULT 0,
    status          TEXT NOT NULL,          -- filed / review / duplicate / ignored
    duplicate_of    INTEGER,
    issues          TEXT,                   -- JSON list of {code, level, msg}
    confidence      TEXT,                   -- JSON {field: 0..1}
    extracted       TEXT,                   -- JSON: what the extractor found
    overrides       TEXT,                   -- JSON: what an admin set by hand (wins over extracted)
    verified        INTEGER NOT NULL DEFAULT 0,
    text            TEXT,
    text_method     TEXT,
    bank_txn_id     INTEGER,
    created_at      TEXT,
    updated_at      TEXT
);
CREATE INDEX IF NOT EXISTS ix_inv_payment ON invoices(payment_date);
CREATE INDEX IF NOT EXISTS ix_inv_status ON invoices(status, paid);
CREATE INDEX IF NOT EXISTS ix_inv_supplier ON invoices(supplier);

CREATE TABLE IF NOT EXISTS suppliers (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,
    aliases     TEXT,                       -- JSON list of names as printed on invoices
    tax_ids     TEXT,                       -- JSON list
    domains     TEXT,                       -- JSON list of sender e-mail domains
    paid_on     TEXT,                       -- rule: issue_date / due_date / fulfilment_date (auto-charged)
    builtin     INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT,
    updated_at  TEXT
);

CREATE TABLE IF NOT EXISTS users (
    username    TEXT PRIMARY KEY,
    pw_hash     TEXT NOT NULL,
    role        TEXT NOT NULL DEFAULT 'admin',   -- admin / viewer
    created_at  TEXT,
    last_login  TEXT
);

CREATE TABLE IF NOT EXISTS sessions (
    token_hash  TEXT PRIMARY KEY,
    username    TEXT NOT NULL,
    csrf        TEXT NOT NULL,
    created_at  TEXT,
    expires_at  TEXT
);

CREATE TABLE IF NOT EXISTS events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    at          TEXT NOT NULL,
    actor       TEXT,
    invoice_id  INTEGER,
    action      TEXT NOT NULL,
    detail      TEXT
);
CREATE INDEX IF NOT EXISTS ix_events_invoice ON events(invoice_id);

CREATE TABLE IF NOT EXISTS seen_messages (
    key         TEXT PRIMARY KEY,
    at          TEXT,
    result      TEXT
);

CREATE TABLE IF NOT EXISTS bank_txns (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    hash         TEXT NOT NULL UNIQUE,
    account      TEXT,
    date         TEXT NOT NULL,
    amount       TEXT NOT NULL,             -- positive = money out
    currency     TEXT,
    counterparty TEXT,
    description  TEXT,
    batch        TEXT,
    imported_at  TEXT,
    invoice_id   INTEGER,
    score        REAL,
    status       TEXT NOT NULL DEFAULT 'unmatched'   -- unmatched / suggested / matched / ignored
);

CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT
);
"""

JSON_FIELDS = ('source_detail', 'issues', 'confidence', 'extracted', 'overrides')
INVOICE_COLUMNS = (
    'sha256', 'file_path', 'original_name', 'source', 'source_detail', 'received_at', 'doc_type',
    'supplier', 'supplier_raw', 'supplier_tax_id', 'invoice_number', 'issue_date', 'fulfilment_date',
    'due_date', 'payment_method', 'amount', 'currency', 'payment_date', 'payment_source', 'paid',
    'status', 'duplicate_of', 'issues', 'confidence', 'extracted', 'overrides', 'verified', 'text',
    'text_method', 'bank_txn_id', 'created_at', 'updated_at')


def connect(path):
    con = sqlite3.connect(str(path), timeout=30)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA busy_timeout = 30000')
    con.execute('PRAGMA foreign_keys = ON')
    return con


def init(path):
    con = connect(path)
    try:
        with con:
            con.executescript(SCHEMA)
            con.execute("INSERT OR IGNORE INTO meta(key, value) VALUES('schema_version', ?)", (str(SCHEMA_VERSION),))
    finally:
        con.close()


def _decode(row):
    if row is None:
        return None
    d = dict(row)
    for k in JSON_FIELDS:
        if k in d:
            d[k] = jload(d[k], {} if k in ('source_detail', 'confidence', 'extracted', 'overrides') else [])
    return d


def _encode(fields):
    out = {}
    for k, v in fields.items():
        if k not in INVOICE_COLUMNS:
            raise KeyError(f'unknown invoice column {k}')
        out[k] = jdump(v) if k in JSON_FIELDS else v
    return out


def get_invoice(con, invoice_id):
    return _decode(con.execute('SELECT * FROM invoices WHERE id = ?', (invoice_id,)).fetchone())


def find_invoices(con, where='1=1', params=(), order='payment_date, supplier, id', limit=None):
    sql = f'SELECT * FROM invoices WHERE {where} ORDER BY {order}'
    if limit:
        sql += f' LIMIT {int(limit)}'
    return [_decode(r) for r in con.execute(sql, params).fetchall()]


def insert_invoice(con, fields):
    f = _encode(fields)
    cols = ', '.join(f)
    qs = ', '.join('?' for _ in f)
    cur = con.execute(f'INSERT INTO invoices ({cols}) VALUES ({qs})', tuple(f.values()))
    return cur.lastrowid


def update_invoice(con, invoice_id, fields):
    if not fields:
        return
    fields = dict(fields)
    fields['updated_at'] = now_iso()
    f = _encode(fields)
    sets = ', '.join(f'{k} = ?' for k in f)
    con.execute(f'UPDATE invoices SET {sets} WHERE id = ?', (*f.values(), invoice_id))


def log_event(con, action, invoice_id=None, actor='bot', detail=None):
    con.execute('INSERT INTO events(at, actor, invoice_id, action, detail) VALUES (?, ?, ?, ?, ?)',
                (now_iso(), actor, invoice_id, action, jdump(detail) if detail is not None else None))


def events(con, invoice_id=None, limit=50):
    if invoice_id is None:
        rows = con.execute('SELECT * FROM events ORDER BY id DESC LIMIT ?', (limit,)).fetchall()
    else:
        rows = con.execute('SELECT * FROM events WHERE invoice_id = ? ORDER BY id DESC LIMIT ?',
                           (invoice_id, limit)).fetchall()
    out = []
    for r in rows:
        d = dict(r)
        d['detail'] = jload(d['detail'], d['detail'])
        out.append(d)
    return out


def meta_get(con, key, default=None):
    r = con.execute('SELECT value FROM meta WHERE key = ?', (key,)).fetchone()
    return jload(r['value'], default) if r else default


def meta_set(con, key, value):
    con.execute('INSERT INTO meta(key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value',
                (key, jdump(value)))
