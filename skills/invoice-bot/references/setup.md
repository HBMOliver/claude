# Setup

## 1. Requirements

- Python 3.9 or newer (macOS, Linux, Windows). No packages are required for the bot itself.
- A PDF text reader, one of:
  - `pdftotext` from poppler (best: keeps table columns). macOS: `brew install poppler`; Debian/Ubuntu: `sudo apt install poppler-utils`; Windows: install "poppler for Windows" and add its `bin` folder to PATH.
  - or `pip install pypdf` (pure Python fallback).
- Optional OCR for scanned invoices: `tesseract` (+ the `hun` language data) and `pdftoppm` (comes with poppler). Without it, scans go to review and you or Claude type the fields in.

`python3 scripts/invoice_bot.py check` reports what is present.

The program can run from this skill folder, or be copied anywhere (copy `scripts/invoice_bot.py` and `scripts/invoicebot/` together). For a scheduled bot, prefer a stable copy (e.g. `~/InvoiceBot/app/`) so updates to the skill do not move it.

## 2. The bot folder

```bash
python3 invoice_bot.py --home ~/InvoiceBot init --company "Your Company Kft." --tax-id 12345678-2-42 \
    --tax-id HU12345678 --domain yourcompany.hu --alias "Your Company" --csv-locale hu
```

| Option | Why |
| --- | --- |
| `--company`, `--alias` | Your company is the buyer on every invoice; the bot uses this to never take it for the supplier, and to notice sales invoices issued by you. |
| `--tax-id` | Your tax numbers (all formats): same reason, and tax numbers are the most reliable way to tell companies apart. |
| `--domain` | Your e-mail domains: a colleague forwarding an invoice is not the supplier. |
| `--currency` | Currency assumed when an invoice shows none (default HUF). |
| `--archive` | Put the organised archive somewhere else, e.g. a shared cloud folder (see 5). |
| `--csv-locale hu` | CSV downloads with `;` and decimal comma, so Hungarian/European Excel opens them in columns. `en` = `,` and decimal point. |

Running `init` again with new options adds to the settings. `config` shows everything; `config KEY VALUE` changes one setting.

Instead of `--home` every time you can set `INVOICEBOT_HOME=~/InvoiceBot`.

## 3. Where invoices come from

### Drop folder (always on)
Anything put in `<bot folder>/inbox/` (PDF, JPG/PNG, saved e-mails `.eml`, ZIP) is collected on the next run and removed from there. Files that contain no invoice go to `inbox/_not_processed/`, never deleted. Good sources: a scanner or phone-scanning app saving to that folder, a synced cloud folder, an e-mail rule that saves attachments.

### Mailbox (IMAP)
```bash
python3 invoice_bot.py imap setup --host imap.example.hu --user szamla@example.hu [--folder INBOX --folder "Számlák"]
python3 invoice_bot.py imap password        # stored in <bot folder>/secrets/imap_password, readable only by you
python3 invoice_bot.py imap test
```
Or put the password in the `INVOICEBOT_IMAP_PASSWORD` environment variable instead.

- **Gmail / Google Workspace**: turn on 2-step verification, create an *app password* (Google Account > Security > App passwords), and make sure IMAP is enabled (Gmail settings > Forwarding and POP/IMAP). Use `imap setup --host imap.gmail.com --user you@domain --gmail`; `--gmail` also restricts the search to messages with attachments (`imap.gmail_query`). To label processed mails: `config imap.gmail_label "Invoices/Processed"`.
- **Microsoft 365 / Outlook.com**: Microsoft has switched off password logins for IMAP. Forward invoice mails to a mailbox that allows IMAP, or let Outlook save attachments into the drop folder (Power Automate "save attachments to OneDrive folder" + sync that folder as the inbox).
- **Hungarian hosting (cPanel, Rackhost, Tárhely.eu, Forpsi, ...)**: usually `mail.<domain>` or the host's IMAP server on port 993 with the mailbox password.
- A dedicated address such as `szamla@yourcompany.hu`, to which suppliers send invoices (and colleagues forward them), works best.

What is collected: new messages from the last `imap.lookback_days` (45) days in `imap.folders`. Attachments that look like invoices are kept (PDFs scored on invoice words, number, total, dates, tax numbers; `collect.min_invoice_score`). Messages are remembered and never fetched twice. Nothing is deleted in the mailbox. Narrow it with `imap.only_from` / `imap.ignore_from` (addresses or domains) or `imap.search` (raw IMAP criteria such as `FROM "billing@x.com"`).

Invoices that only come as a download link in the e-mail are not fetched; save the PDF into the inbox folder (or ask Claude to).

## 4. Running automatically

`python3 invoice_bot.py schedule [--every 30] [--serve]` prints ready-to-use setups for this computer, with the right paths:

- **cron** (Linux/macOS): `*/30 * * * * python3 .../invoice_bot.py --home ~/InvoiceBot run`
- **launchd** (macOS): a LaunchAgent plist that runs every 30 minutes.
- **systemd** (Linux server): a user service running `serve --collect-every 30`: the admin panel stays up and collects on a timer, one process for everything.
- **Task Scheduler** (Windows): a `schtasks /Create` line.

A run that finds another run in progress does nothing, so overlapping schedules are safe. Logs: `<bot folder>/logs/invoicebot.log`.

With Claude: a scheduled task can run `invoice_bot.py run` daily and then work the review queue (see SKILL.md, "Running it").

## 5. A shared archive folder

The archive (`archive_dir`) can live in a synced folder so other administrators see it without the panel, for example:
- Google Drive for desktop: `~/Library/CloudStorage/GoogleDrive-<you>/Shared drives/Finance/Invoices` (macOS) or `G:\Shared drives\Finance\Invoices` (Windows)
- Dropbox / OneDrive folders likewise.

`init --archive "<path>"` (or `config archive_dir "<path>"` followed by `verify --fix` after moving the existing files). Every month folder carries a `_summary.csv`. Keep the bot folder itself (with `invoicebot.db`) on a local disk: SQLite databases do not belong in sync folders.

## 6. Admin panel

```bash
python3 invoice_bot.py users add oliver                 # admin
python3 invoice_bot.py users add konyvelo --role viewer # can view and download only
python3 invoice_bot.py serve                            # http://127.0.0.1:8765
```
Remote access, HTTPS and security: `admin-panel.md`.

## 7. Backups

Back up the whole bot folder (ledger + archive + settings) together, e.g. with Time Machine or a nightly copy. The archive alone is also readable without the bot: every file name carries date, supplier and number, and every folder has `_summary.csv`.
