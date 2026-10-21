"""Admin accounts and login sessions.

Passwords are stored as scrypt hashes (PBKDF2-SHA256 where scrypt is unavailable). Session tokens are
random 256-bit values; only their SHA-256 is stored. Roles: admin (everything) and viewer (browse and
download only, e.g. for the accountant).
"""
import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

from .util import now_iso

ROLES = ('admin', 'viewer')
MIN_PASSWORD = 10


def _b64(b):
    return base64.b64encode(b).decode('ascii')


def hash_password(pw):
    salt = secrets.token_bytes(16)
    try:
        h = hashlib.scrypt(pw.encode('utf-8'), salt=salt, n=2 ** 14, r=8, p=1, dklen=32)
        return f'scrypt$16384$8$1${_b64(salt)}${_b64(h)}'
    except (AttributeError, ValueError):
        h = hashlib.pbkdf2_hmac('sha256', pw.encode('utf-8'), salt, 600_000)
        return f'pbkdf2_sha256$600000${_b64(salt)}${_b64(h)}'


def verify_password(pw, stored):
    try:
        parts = stored.split('$')
        if parts[0] == 'scrypt':
            n, r, p = int(parts[1]), int(parts[2]), int(parts[3])
            salt, want = base64.b64decode(parts[4]), base64.b64decode(parts[5])
            got = hashlib.scrypt(pw.encode('utf-8'), salt=salt, n=n, r=r, p=p, dklen=len(want))
        elif parts[0] == 'pbkdf2_sha256':
            it, salt, want = int(parts[1]), base64.b64decode(parts[2]), base64.b64decode(parts[3])
            got = hashlib.pbkdf2_hmac('sha256', pw.encode('utf-8'), salt, it)
        else:
            return False
        return hmac.compare_digest(got, want)
    except (ValueError, IndexError, TypeError):
        return False


_DUMMY = None


def dummy_verify(pw):
    """Spend the same time as a real check, so unknown user names cannot be told apart by timing."""
    global _DUMMY
    if _DUMMY is None:
        _DUMMY = hash_password(secrets.token_hex(8))
    verify_password(pw, _DUMMY)


def check_password_rules(pw):
    if len(pw) < MIN_PASSWORD:
        raise ValueError(f'password must be at least {MIN_PASSWORD} characters')


def generate_password():
    return secrets.token_urlsafe(12)


def valid_username(name):
    return bool(name) and len(name) <= 64 and all(c.isalnum() or c in '._-@' for c in name)


def add_user(con, username, password, role='admin'):
    if not valid_username(username):
        raise ValueError('user name: letters, digits and . _ - @ only')
    if role not in ROLES:
        raise ValueError(f'role must be one of {ROLES}')
    check_password_rules(password)
    if con.execute('SELECT 1 FROM users WHERE username = ?', (username,)).fetchone():
        raise ValueError(f'user {username} already exists')
    con.execute('INSERT INTO users(username, pw_hash, role, created_at) VALUES (?, ?, ?, ?)',
                (username, hash_password(password), role, now_iso()))


def set_password(con, username, password):
    check_password_rules(password)
    cur = con.execute('UPDATE users SET pw_hash = ? WHERE username = ?', (hash_password(password), username))
    if not cur.rowcount:
        raise KeyError(f'no user {username}')
    con.execute('DELETE FROM sessions WHERE username = ?', (username,))


def set_role(con, username, role):
    if role not in ROLES:
        raise ValueError(f'role must be one of {ROLES}')
    if not con.execute('UPDATE users SET role = ? WHERE username = ?', (role, username)).rowcount:
        raise KeyError(f'no user {username}')


def remove_user(con, username):
    if not con.execute('DELETE FROM users WHERE username = ?', (username,)).rowcount:
        raise KeyError(f'no user {username}')
    con.execute('DELETE FROM sessions WHERE username = ?', (username,))


def list_users(con):
    return [dict(r) for r in con.execute('SELECT username, role, created_at, last_login FROM users ORDER BY username')]


def authenticate(con, username, password):
    row = con.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    if row is None:
        dummy_verify(password)
        return None
    if not verify_password(password, row['pw_hash']):
        return None
    con.execute('UPDATE users SET last_login = ? WHERE username = ?', (now_iso(), username))
    return dict(row)


def _token_hash(token):
    return hashlib.sha256(token.encode('ascii', 'ignore')).hexdigest()


def new_session(con, username, hours=12):
    token = secrets.token_urlsafe(32)
    csrf = secrets.token_urlsafe(24)
    now = datetime.now(timezone.utc)
    con.execute('INSERT INTO sessions(token_hash, username, csrf, created_at, expires_at) VALUES (?, ?, ?, ?, ?)',
                (_token_hash(token), username, csrf, now.isoformat(), (now + timedelta(hours=hours)).isoformat()))
    con.execute('DELETE FROM sessions WHERE expires_at < ?', (now.isoformat(),))
    return token


def session_user(con, token):
    """(user row with role, csrf token) for a valid session cookie, else (None, None)."""
    if not token or len(token) > 200:
        return None, None
    r = con.execute('SELECT s.username, s.csrf, s.expires_at, u.role FROM sessions s JOIN users u '
                    'ON u.username = s.username WHERE s.token_hash = ?', (_token_hash(token),)).fetchone()
    if r is None or r['expires_at'] < datetime.now(timezone.utc).isoformat():
        return None, None
    return {'username': r['username'], 'role': r['role']}, r['csrf']


def end_session(con, token):
    if token:
        con.execute('DELETE FROM sessions WHERE token_hash = ?', (_token_hash(token),))
