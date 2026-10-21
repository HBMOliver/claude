# Troubleshooting

| Problem | Fix |
| --- | --- |
| `No invoice bot set up in ...` | Run `init` with that `--home`, or set `INVOICEBOT_HOME`. |
| Every invoice lands in review with "No text could be read" | No PDF reader: install poppler (`pdftotext`) or `pip install pypdf`; then `reextract --all`. For real scans install tesseract (+ `hun` data) or fill the fields in by hand. |
| Supplier is my own company / the buyer | Set `init --company ... --tax-id ... --alias ...` with every spelling of your name, then `reextract --all`. |
| Supplier name is wrong or too long | Correct it once (`update ID --supplier "Name"` or the panel); the bot remembers the printed name, tax number and sender domain. Rename everywhere: `suppliers rename OLD NEW`. |
| Wrong amount (net instead of gross, or a HUF conversion) | Correct it; if it happens for one supplier's layout every time, send Claude the text (`show ID --text`) to adjust the rules in `extract.py`. |
| Day and month swapped (05/10 vs 10/05) | `config date_order MDY` (or `DMY`) and `reextract` the affected ones; or correct the date. |
| Card-paid invoices wait in `_unpaid` | The invoice does not say how it was paid: give the supplier a rule, `suppliers add "Name" --paid-on issue_date`, or confirm with a bank statement. |
| Transfer invoices never leave `_unpaid` | Import the bank statement (`bank file.csv`), or mark them paid. Suggestions below score 75 need a confirmation (`bank-link`). |
| Bank import: "Could not find the header row" | Export the statement as CSV (not PDF/XLS) with column headers; the file needs a date and an amount (or debit) column. |
| IMAP: login failed | Gmail/Workspace: app password + IMAP enabled; Microsoft 365: password IMAP is disabled by Microsoft (see setup.md 3); check host/port (`imap test`). |
| IMAP: mails are skipped | Check `logs/invoicebot.log`. PDFs that do not look like invoices are skipped (`collect.min_invoice_score`, default 2); for a "link only" invoice save the PDF into the inbox. |
| A file was moved by hand, or a re-file was interrupted | `verify` lists the differences; `verify --fix` re-attaches files found elsewhere in the archive (by their content) and puts every invoice where its data says. Stray files that belong to no invoice: drop them in the inbox. |
| Something landed in `inbox/_not_processed/` | The run report says why (no invoice in it, a spreadsheet or image next to the PDFs, an unreadable ZIP member, a ZIP inside a ZIP). Whatever was imported from it is in the archive; fix and drop the rest again. |
| A bank payment was not applied automatically | It fits more than one invoice almost equally (e.g. monthly invoices of the same amount): confirm the right pair on the Bank statement page or with `bank-link`. |
| Panel: "Unexpected Host header" | Add the host name you use: `config admin.allowed_hosts '["name"]'`. |
| Panel: "Cross-site form submission refused" behind a proxy | The proxy must pass the original Host header (nginx: `proxy_set_header Host $host;`), or set `admin.trust_proxy` so `X-Forwarded-Host` is used. |
| Forgot the admin password | `users passwd NAME` on the command line. |
| "Another collection run is in progress" | A scheduled run is busy; it ends by itself. A stale lock disappears when that process ends. |
