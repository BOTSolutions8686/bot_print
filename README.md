# BOT Print

Reusable ERPNext print extras for BOT Solutions sites.

First use: **Zhengmao** (`zhengmao.metadaftr.com`) — SAR invoice stays SAR for ZATCA; Multi Currency PDF can show a **manual** USD (or other) amount at the bottom.

This does **not** change invoice calculations, GL, or ZATCA XML.

## What it adds

On **Sales Invoice** (Currency and Price List area):

| Field | Purpose |
|--------|--------|
| **PDF Display Currency** | e.g. USD |
| **PDF Display VAT Amount** | Manual VAT for the PDF |
| **PDF Display Total Amount** | Manual total for the PDF |

If currency and both amounts are empty, those two rows stay SAR (`ريال`).

On migrate, the app patches the bottom tax rows (`القيمة الخاضعة للضريبة` / VAT 15%) on print formats named `Multiple Currency` or `Multi Currency`. SAR totals above that stay SAR. No extra table is added.

## Install (Frappe v15)

```bash
cd ~/frappe-bench
bench get-app https://github.com/BOTSolutions8686/bot_print.git --branch main
bench --site zhengmao.metadaftr.com install-app bot_print
bench --site zhengmao.metadaftr.com migrate
bench --site zhengmao.metadaftr.com clear-cache
```

If the site folder name differs, use that site name (`ls sites`).

Re-inject into a print format after HTML edits:

```python
from bot_print.install import inject_pdf_display_block
print(inject_pdf_display_block("Zhengmao Multiple Currency"))
```

## How users print

1. Keep invoice **Currency = SAR**.
2. Fill **PDF Display Currency**, **PDF Display VAT Amount**, and **PDF Display Taxable Amount**.
3. Print with **Zhengmao Multiple Currency**. The two bottom tax rows show that currency and amounts; the SAR totals above stay SAR.

## License

MIT
