---
name: invoice-bot
description: Automated invoice bot. Collects incoming invoices (mailbox via IMAP, a drop folder, uploads), identifies supplier, invoice number, amount and payment date (Hungarian, English and German invoices), renames them YYYY-MM-DD_Supplier_InvoiceNumber.pdf, files them by payment month and year, confirms payments from bank statements, and gives administrators a web panel to check and download invoices. Use for setting up or running invoice collection, számla / bookkeeping prep, monthly accountant exports, or questions about received invoices.
---

# Invoice Bot

A self-contained invoice archive that runs on the user's computer or server. It collects invoices automatically, reads them, names them `YYYY-MM-DD_Supplier_InvoiceNumber.pdf` where the date is the **payment date**, and files them into `archive/<year>/<year>-<month>/` by the month they were paid in. Administrators browse, correct and download them in a web panel; a viewer role lets the accountant download without changing anything.

You (Claude) set it up, run it, and handle what the rules cannot: scanned invoices without a text layer, uncertain fields, and questions about the archive. Everything runs through one command, `scripts/invoice_bot.py` (Python 3.9+, standard library; reading PDFs needs poppler's `pdftotext` or the `pypdf` package).

```bash
python3 scripts/invoice_bot.py --home "<bot folder>" <command>     # or set INVOICEBOT_HOME once
python3 scripts/invoice_bot.py --help                               # all commands
```

## What it does (and where it is in the code)

| Requirement | How |
| --- | --- |
| Collect invoices automatically | `run`: IMAP mailbox (attachments, also inside forwarded mails and ZIPs) + the `inbox/` drop folder; `serve --collect-every 30` or cron repeats it (`collect.py`) |
| Identify supplier, amount, payment date, number | Label-based reading of the PDF text in HU/EN/DE with column-aware tables, buyer/seller blocks, known-supplier registry (`extract.py`, `suppliers.py`) |
| Rename consistently | `{date}_{supplier}_{number}.pdf`, ASCII-safe, collision-safe (`pipeline.py`) |
| Organise by payment date, by month and year | `archive/2026/2026-09/`; unconfirmed payments wait in `archive/_unpaid/` (`pipeline.py`) |
| Admins download invoices | Web panel: one file, a month, a year or a selection as ZIP with a CSV summary; `export` on the command line (`web.py`, `export.py`) |

How the payment date is decided, in order: an admin marked it paid > a matching bank-statement payment > a payment date printed on the invoice ("Date paid", "Fizetés dátuma") > the supplier's payment rule (auto-charged suppliers) > card/cash/PayPal/online payment or a PAID stamp or receipt = paid on the invoice date > direct debit = paid on the due date. Anything else (typically bank transfers) is **not confirmed**: it waits in `_unpaid/` named with its due date until a bank statement, an admin or a rule confirms it, then moves into its payment month. Details: `references/how-it-works.md`.

## First-time setup

Read `references/setup.md` for the per-platform details. In short, ask the user (in one message, AskUserQuestion when available) for what you do not know yet:
1. **Where should the bot live?** A local folder for the bot (e.g. `~/InvoiceBot`). The archive can be elsewhere, e.g. a shared Google Drive / Dropbox / OneDrive folder so other admins see it too (`init --archive "<path>"`). The ledger database must stay on a local disk.
2. **Their company** (the buyer on every invoice, never the supplier): legal name, other names, tax numbers, e-mail domain(s).
3. **Where invoices arrive**: a mailbox (IMAP host, user; Gmail/Google Workspace need IMAP enabled and an app password), and/or a folder.
4. **Admins**: who logs into the panel; whether the accountant needs a view-only login.

Then:
```bash
python3 scripts/invoice_bot.py check                                   # tools present? installs nothing
python3 scripts/invoice_bot.py --home ~/InvoiceBot init --company "HB Marketing Kft." --tax-id 12345678-2-42 \
    --domain hbmarketing.hu --csv-locale hu [--archive "<shared folder>"]
python3 scripts/invoice_bot.py --home ~/InvoiceBot imap setup --host imap.gmail.com --user szamla@example.hu --gmail
python3 scripts/invoice_bot.py --home ~/InvoiceBot imap password      # the USER types it (hidden prompt)
python3 scripts/invoice_bot.py --home ~/InvoiceBot imap test
python3 scripts/invoice_bot.py --home ~/InvoiceBot users add oliver    # prompts for a password (10+ chars)
python3 scripts/invoice_bot.py --home ~/InvoiceBot users add konyvelo --role viewer
python3 scripts/invoice_bot.py --home ~/InvoiceBot run                 # first collection
python3 scripts/invoice_bot.py --home ~/InvoiceBot schedule            # prints cron / launchd / systemd / Task Scheduler setups
```
- Passwords: let the user type them in their own terminal (`imap password`, `users add`). If they can only paste one into the chat, use `--password-stdin` / `imap password --stdin` and say it stays in the chat history; prefer an app password they can revoke. For a quick start, `users add NAME --generate` prints a strong password once; tell them to change it under Account in the panel.
- Want to show it first? `python3 scripts/invoice_bot.py demo` builds a sample bot in `~/InvoiceBot-demo` with seven typical invoices and two bank statements.
- Suppliers that charge a card automatically (Google, Meta ads, SaaS) usually print "paid" or the card on the invoice, so they are confirmed without help. If one is not, give it a rule: `suppliers add "Google" --paid-on issue_date`.

## Running it

Every run prints what happened; `--json` on `run`, `status`, `list`, `show`, `update`, `bank`, `export` gives machine-readable output.

1. `status` first: counts, last collection, what is unpaid or waiting for review.
2. `run` to collect now (the schedule does this on its own).
3. **Review queue** (`list --status review`): invoices missing a field stay in `archive/_review/` under their original name. For each one, look at the file yourself (`show ID` gives the path; read the PDF) and fill in what is missing:
   `update ID --supplier "Kovács és Társa" --number E-2026-118 --amount 127000 --currency HUF --issue-date 2026-09-15 --due-date 2026-09-23`
   The file is renamed and moved the moment the invoice is complete. Corrections teach the supplier registry (the printed name, tax number and sender domain), so the next invoice from that supplier is named the same way. Ask the user only when the document itself does not tell you.
   Also look at filed invoices with warnings (`list --status filed --json`, issues with level `warn`): fix or leave them.
4. **Payments**: transfer invoices wait in `_unpaid/`. Ask for the bank statement export (CSV) and run `bank statement.csv`: confident, unambiguous matches are applied; the rest (including payments that fit several invoices of the same amount) are listed as suggestions to confirm with `bank-link INVOICE PAYMENT` after checking with the user. Or mark directly: `paid ID --date 2026-10-03`.
5. **For the accountant**: `export --month 2026-09` makes `exports/invoices_2026-09.zip` (all invoices paid that month + `summary.csv`). Send the file to the user, or point them to the panel's month page.
6. **Admin panel**: `serve` (add `--collect-every 30` to also collect on a timer) and open `http://127.0.0.1:8765`. Remote access and roles: `references/admin-panel.md`.

Questions like "what did we pay Google in September?" or "which invoices are overdue?": answer from `list --month 2026-09 --supplier Google --json` and `list --status unpaid --json`, not from memory.

## Rules

- Change invoices only through the bot (`update`, `paid`, `unpaid`, the panel): never rename or move files in the archive by hand, or the ledger and the folders disagree (`verify` reports it, `verify --fix` re-attaches moved files by their content and re-files).
- Correcting a supplier teaches the registry only when the new name is a better name for the same company; when the bot read the wrong company, the correction stays on that invoice.
- Never invent field values. A field you cannot read from the document stays empty and the invoice stays in review.
- The proforma / díjbekérő, quotes and duplicates are kept under `_other/` and `_duplicates/`, not in the monthly archive; `update ID --restore` / `--not-duplicate` if the bot was wrong.
- The bot never deletes or moves e-mails; IMAP is read-only unless `imap.mark_seen` or `imap.gmail_label` is set.
- Keep the ledger (`invoicebot.db`) on a local disk; back up the bot folder (ledger + archive) together.
- Settings: `config` shows them all, `config KEY VALUE` changes one (`config payment.unconfirmed estimate` files unpaid invoices by due date instead of holding them). Changing naming, folders or payment settings re-files everything.

## Files

- `scripts/invoice_bot.py`: the command; `scripts/invoicebot/`: the program (`cli`, `collect`, `extract`, `suppliers`, `pipeline`, `bank`, `export`, `web`, `views`, `auth`, `db`, `config`, `textract`, `util`, `samples`, `pdfwriter`; `assets/` holds the panel's CSS/JS, its two OFL fonts and the well-known supplier list)
- `references/setup.md`: install, company settings, mailboxes per provider, schedules, shared archive folders, backups
- `references/how-it-works.md`: how each field is found, naming and folders, payment-date rules, statuses, duplicates, bank matching, all settings
- `references/admin-panel.md`: pages, roles, downloads, remote access and security
- `references/troubleshooting.md`: fixes for common problems
- `tests/`: `python3 -m unittest discover -s tests` (the corpus test needs reportlab)
