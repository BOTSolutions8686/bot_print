# BOT Print

Reusable ERPNext print extras for BOT Solutions sites.

First use: **Zhengmao** (`zhengmao.metadaftr.com`) — SAR invoice stays SAR for ZATCA; Multi Currency PDF can show USD (or other) on the last two tax rows.

This does **not** change invoice calculations, GL, or ZATCA XML.

## What it adds

On **Sales Invoice**, collapsible **PDF Foreign Amount (Print only)** (below Currency and Price List):

| Field | Purpose |
|--------|--------|
| **PDF Display Currency** | e.g. USD. Leave empty to keep SAR on the PDF. |
| **Exchange Rate** | Like `1 USD = [?] SAR`. Filled from **Currency Exchange** if a row exists. You can type freely. Missing rate does **not** show an error. |
| **PDF Display VAT Amount** | Auto: SAR VAT ÷ rate |
| **PDF Display Taxable Amount** | Auto: SAR taxable ÷ rate |

Add other currencies under **Currency Exchange** on the site when needed.

If currency is empty, those two rows stay SAR (`ريال` / `بالريال`). If USD, Arabic labels and the currency column use USD.

## Install (Frappe v15)

```bash
cd ~/frappe-bench
bench get-app https://github.com/BOTSolutions8686/bot_print.git --branch main
bench --site zhengmao.metadaftr.com install-app bot_print
bench --site zhengmao.metadaftr.com migrate
bench --site zhengmao.metadaftr.com clear-cache
bench restart
```

If the site folder name differs, use that site name (`ls sites`).

Re-inject into a print format after HTML edits:

```python
from bot_print.install import inject_pdf_display_block
print(inject_pdf_display_block("Zhengmao Multiple Currency"))
```

## How users print

1. Keep invoice **Currency = SAR**.
2. Open **PDF Foreign Amount (Print only)**, set **PDF Display Currency** (USD). **Exchange Rate** fills from Currency Exchange (or type `3.75`). Amounts fill automatically.
3. Print with **Zhengmao Multiple Currency**.

## License

MIT
