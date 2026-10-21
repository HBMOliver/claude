# How it works

## The life of an invoice

1. **Collected** from the mailbox, the inbox folder, an upload or `add`. Identical files (same bytes) are recognised and skipped.
2. **Read**: the PDF's text is extracted with its layout (`pdftotext -layout`, else pypdf, else OCR).
3. **Identified**: supplier, invoice number, dates, total, currency, payment method, paid stamps (below).
4. **Resolved**: the effective values are what an admin typed (always wins) over what was read; then the payment date is decided.
5. **Named and filed** according to its status. Every later change (an edit, a bank match, a supplier rule) re-runs 4 and 5, so name and folder always match the current facts. Every change is in the history (`show ID`, the panel).

## Finding the fields

The text is scanned line by line for labels in Hungarian, English and German (some French and Italian). Matching ignores case and accents. A label's value is taken from the same line (the first value to its right) or, for table headers, from the line below in the same column. When a header row holds several date labels and the next row holds as many dates, they are paired in order.

| Field | Labels (examples) | Notes |
| --- | --- | --- |
| Invoice number | Számla sorszáma, Számlaszám, Sorszám, Invoice number / No. / #, Rechnungsnummer | "Eredeti számla" / "Original invoice" (a credit note quoting another invoice) is skipped. A title like `SZÁMLA 2026-00077` counts too. |
| Invoice date | Számla kelte, Kiállítás dátuma, Kelt, Invoice date, Date of issue, Rechnungsdatum | Without a label: the first date that is not part of a period. A receipt's paid date stands in. |
| Delivery date | Teljesítés dátuma, Date of supply, Leistungsdatum | |
| Due date | Fizetési határidő, Esedékesség, Due date, Payment due, Fälligkeitsdatum, Zahlbar bis | "Payment terms: 14 days" / "Net 30" is kept as terms (used for the expected date). |
| Paid date | Fizetés dátuma, Kifizetve, Date paid, Paid on, Bezahlt am | A "payment date" in the future is treated as a due date. |
| Total | Fizetendő, Végösszeg, Bruttó végösszeg, Összesen, Total due, Amount due, Grand total, Total (incl. VAT), Amount paid, Gesamtbetrag | Lines about net amounts, VAT, subtotals, discounts, carried-forward totals, exchange rates and HUF conversions are excluded. On an "Összesen" line with net, VAT and gross, the largest is taken. Credit notes are stored negative. |
| Currency | the total's symbol or code (Ft, HUF, €, EUR, $, £, ...), "Pénznem: EUR", else the most frequent one, else `default_currency` | |
| Payment method | Fizetési mód, Payment method, Paid with, Zahlungsart | Átutalás/transfer, bankkártya/card, készpénz/cash, PayPal, csoportos beszedés/direct debit, utánvét/COD, online (SimplePay, Barion, Stripe). |
| Paid stamp | PAID, Fizetve, Kiegyenlítve, Pénzügyileg rendezve, Payment received, Bezahlt, or the document is a receipt | Negations ("unpaid", "not paid", "nem fizetett", "Amount paid 0.00") do not count. |

Dates are read in all common forms: `2026.09.15.`, `2026. 09. 15.`, `2026-09-15`, `15.09.2026`, `15/09/2026`, `09/15/2026`, `15 Sep 2026`, `September 15, 2026`, `2026. szeptember 15.`. For dates like `05/10/2026` the document decides (another date on it that can only be day-first or month-first); otherwise `date_order` (DMY), except US-dollar invoices with `/`, which are read month-first.

### The supplier

Candidates are collected and the strongest wins; candidates naming the same company reinforce each other:

1. **The supplier registry**: a known name as printed (e.g. "Google Ireland Limited" is filed as "Google"), a known tax number, or a known sender domain. ~65 well-known suppliers come built in; every admin correction adds to it.
2. **The seller block**: the text under or after "Eladó", "Szállító", "Szolgáltató", "Supplier", "Seller", "From", "Verkäufer" ... cut out by column, so a two-column "Eladó | Vevő" header works.
3. **Company names with a legal form** (Kft., Bt., Zrt., Nyrt., e.v., Ltd, LLC, Inc., GmbH, SARL, B.V., ...), preferring the top of the page.
4. **The e-mail sender's** display name or domain (ignoring invoicing platforms like Stripe, Számlázz.hu, Billingo and your own domain).
5. The letterhead (weakest).

The buyer's block ("Vevő", "Bill to", "Customer", "Rechnungsempfänger") and your own company are never candidates. Footer lines such as "Készült a ... számlázó programmal" are ignored, as are banks named next to bank account numbers. Item lines that mention other companies ("Google Ads kampánykezelés") do not count, because they carry no legal form and sit in no seller block.

The **name used in file names** is the registry name if known, else the printed name without the legal form and without trailing Hungarian activity words: "Kovács és Társa Szolgáltató és Kereskedelmi Kft." becomes "Kovács és Társa". ALL-CAPS names are converted to normal case. In file names accents are transliterated (`naming.ascii`).

### Confidence

Each field gets a confidence from 0 to 1 (shown in `show`). Missing supplier, number, total or date, or a supplier below 0.45, puts the invoice in **review**. A low-confidence value that is still likely right (supplier 0.45-0.65, number or amount below 0.6, an unlabelled invoice date) files the invoice with a **warning**, listed under "To check" until someone saves it.

## The payment date

Resolved in this order; the first rule that applies wins:

| Source (`payment_source`) | When | Confirmed? |
| --- | --- | --- |
| `manual` | an admin entered "Paid on" / `paid ID --date` | yes |
| `bank` | matched to an outgoing payment in an imported bank statement | yes |
| `invoice` | the document prints a payment date | yes |
| `supplier_rule` | the supplier has `paid_on` set (issue / due / delivery date) | yes |
| `payment_method` | card, cash, PayPal, online (`payment.immediate_methods`): the invoice date; COD: the delivery date | yes |
| `paid_stamp` | the document says paid, or is a receipt: the invoice date | yes |
| `direct_debit` | direct debit (csoportos beszedés): the due date (`payment.direct_debit_on_due_date`) | yes |
| `expected_due` / `expected_terms` / `expected_issue` | otherwise: the due date, else invoice date + terms, else the invoice date | **no** |

Unconfirmed invoices are "waiting for payment". With `payment.unconfirmed = hold` (default) they wait in `_unpaid/`; with `estimate` they are filed in the month of their expected date and flagged as expected in summaries and the panel. `unpaid ID` (or "Mark as not paid") overrides every automatic confirmation except a bank match.

## Names and folders

File name: `naming.pattern`, default `{date}_{supplier}_{number}` + the original extension, where `{date}` is the payment date (or the expected one). Also available: `{issue_date}`, `{due_date}`, `{amount}`, `{currency}`. Fields never contain `_` (it separates them) or characters invalid on Windows; `/` in invoice numbers becomes `-` (`HBM/2026/0042` → `HBM-2026-0042`). Two invoices that would get the same name get `_2`, `_3`.

| Status | Folder (`folders.*`) | File name |
| --- | --- | --- |
| filed, paid | `{yyyy}/{yyyy}-{mm}` (`folders.layout`) of the payment date | standard |
| filed, not paid | `_unpaid` (or the month of the expected date with `estimate`) | standard, expected date |
| review | `_review` | `<id>_<original name>` |
| duplicate | `_duplicates` | `<id>_<original name>` |
| ignored (proforma, quote, "not an invoice") | `_other` | `<id>_<original name>` |

Each folder carries a `_summary.csv` (payment date, supplier, number, amount, currency, dates, how the payment date is known, method, type, supplier tax number, file), refreshed after every change.

## Duplicates

The same file twice is skipped at collection. A different file with the same supplier and invoice number (a re-sent invoice) is kept as a duplicate of the first, in `_duplicates/`. If they really are different invoices: `update ID --not-duplicate`.

## Bank statements

`bank statement.csv` (or the Bank statement page) reads a CSV export: the encoding (UTF-8, Windows-1250), delimiter and header row are detected and the columns recognised by name: date (Könyvelés dátuma, Booking date, Completed Date, Buchungstag, ...), amount or debit/credit, currency, partner/counterparty and reference (Közlemény, Description, Reference, Verwendungszweck). Only money going out is used; payments are remembered, so overlapping exports are harmless.

Matching an unpaid invoice requires the same currency and amount (±1 HUF, ±0.01 otherwise) and a payment between 5 days before the invoice date and 120 days after the due date. Score: 50 for the amount, +40 if the invoice number appears in the reference, +up to 30 for the supplier's name in the counterparty or reference, +8 within three days of the due date, minus a little for every day away from the due date. 75 or more is applied at once; 50 to 75 is a suggestion to confirm (`bank-link`) or dismiss. Payments imported earlier are also checked against every new invoice as it arrives.

## Settings (invoicebot.json)

| Key | Default | |
| --- | --- | --- |
| `company.name / aliases / tax_ids / email_domains` | empty | your company (see setup) |
| `archive_dir`, `inbox_dir`, `exports_dir` | `archive`, `inbox`, `exports` | relative to the bot folder or absolute |
| `default_currency` | `HUF` | |
| `date_order` | `DMY` | for ambiguous numeric dates |
| `naming.pattern / ascii / space / max_supplier / max_number` | `{date}_{supplier}_{number}`, true, `-`, 40, 40 | |
| `folders.layout / unpaid / review / duplicates / other` | `{yyyy}/{yyyy}-{mm}`, `_unpaid`, `_review`, `_duplicates`, `_other` | `{yy}`, `{dd}` also work |
| `payment.unconfirmed` | `hold` | or `estimate` |
| `payment.immediate_methods` | card, cash, paypal, online | |
| `payment.direct_debit_on_due_date` | true | |
| `collect.include_images / max_attachment_mb / min_invoice_score` | false, 25, 2 | |
| `imap.*` | off | see setup.md |
| `csv.delimiter / decimal` | `,` `.` | `init --csv-locale hu` sets `;` `,` |
| `admin.host / port / session_hours / secure_cookies / collect_every_minutes / max_upload_mb / allowed_hosts / trust_proxy` | 127.0.0.1, 8765, 12, false, 0, 50, [], false | see admin-panel.md |
| `month_summaries` | true | `_summary.csv` per folder |
| `ocr.enabled / languages` | true, `hun+eng+deu` | when tesseract is installed |
| `pdf_max_pages` | 10 | pages read per PDF |
