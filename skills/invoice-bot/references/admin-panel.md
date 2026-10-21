# Admin panel

```bash
python3 invoice_bot.py users add <name> [--role viewer]   # at least one admin first
python3 invoice_bot.py serve [--port 8765] [--collect-every 30]
```
Open `http://127.0.0.1:8765`.

## Roles

| Role | Can |
| --- | --- |
| admin | everything: correct fields, mark paid / not paid, upload, import bank statements, set supplier rules, run a collection, download |
| viewer | browse, search and download only (for the accountant) |

Manage logins on the command line: `users list | add NAME [--role viewer] | passwd NAME | role NAME --role admin | remove NAME`. Everyone can change their own password under Account. Passwords need 10+ characters.

## Pages

- **Overview**: what was paid this month (per currency), what needs checking, what is waiting for payment, possible bank matches, the last collection (with "Collect now"), the archive as a year-by-month grid, and the latest arrivals.
- **Month** (click a month): every invoice paid that month by payment date, how the date is known, and the file. "Download <month> (ZIP)" gives all files plus `summary.csv`; "Summary (CSV)" the table only; tick rows for "Download selected (ZIP)". Unpaid invoices expected that month are listed below with a "Paid" button.
- **To check**: invoices in review (what is missing) and filed invoices with warnings.
- **Waiting for payment**: unconfirmed invoices by due date, overdue days, and a date + "Paid" button per row.
- **Invoice**: the PDF next to its fields. "Save changes" stores what you changed (marked "set by hand"), renames and moves the file and teaches the supplier registry. Also: mark paid / not paid, remove a bank match, read the file again, not an invoice / move back, not a duplicate; the bank payment it was matched to; the full history; the text the bot read.
- **Upload**: PDFs, photos, `.eml` and ZIP files; each is filed like a collected one.
- **Bank statement**: upload a CSV export; confident matches are applied, the others listed to confirm or dismiss.
- **Suppliers**: names on invoices, tax numbers, e-mail domains, and the payment rule for auto-charged suppliers.
- **Other documents**: duplicates, proformas, quotes and files marked as not an invoice.
- **Search**: supplier, invoice number, original file name, or an amount (`127000`, `127 000`, `1.234,56`).

Every download (single file, month, year, selection) and every change is written to the history with the user's name.

## Reaching it from other computers

By default the panel listens on 127.0.0.1 (this computer only) and only answers to `localhost`/`127.0.0.1` host names. For access from elsewhere use one of:

1. **A private network** such as Tailscale: run `serve --host 0.0.0.0` and set `config admin.allowed_hosts '["my-mac.tailnet-name.ts.net"]'`.
2. **An HTTPS reverse proxy** (Caddy, nginx) on a server:
   ```
   invoices.example.hu {
       reverse_proxy 127.0.0.1:8765
   }
   ```
   then `config admin.secure_cookies true`, `config admin.allowed_hosts '["invoices.example.hu"]'` and, so the real client address is used for login throttling, `config admin.trust_proxy true` (only behind a proxy you control). Caddy passes the original Host header; with nginx add `proxy_set_header Host $host;` and `proxy_set_header X-Forwarded-For $remote_addr;`.

Never expose the plain HTTP port to the internet.

## Security in short

- Passwords stored as scrypt hashes; sessions are random 256-bit tokens (only their hash is stored) in HttpOnly, SameSite=Strict cookies, ending after `admin.session_hours` (12) or at logout; changing a password logs that user out everywhere.
- Every form carries a CSRF token; cross-site form posts are refused (Origin check); the login form has its own token.
- 8 failed logins from one address lock it out for 15 minutes; unknown user names cost the same time as wrong passwords.
- Strict Content-Security-Policy (no inline scripts or styles, no third-party resources), `nosniff`, same-origin framing only, `no-store` caching for pages and downloads.
- Files are served by ledger id only, from inside the archive; uploads are checked by content (PDF/image/e-mail/ZIP), ZIPs are size-limited and their paths ignored.
