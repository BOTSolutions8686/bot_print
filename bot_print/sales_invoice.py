import frappe
from frappe.utils import flt, nowdate


def set_pdf_foreign_amounts(doc, method=None):
	ccy = (doc.get("custom_pdf_display_currency") or "").strip()
	if not ccy:
		return

	company_ccy = doc.get("company_currency") or frappe.get_cached_value(
		"Company", doc.company, "default_currency"
	)
	rate = flt(doc.get("custom_pdf_display_exchange_rate"))
	if not rate:
		rate = lookup_pdf_exchange_rate(ccy, company_ccy, doc.get("posting_date"))
		if rate:
			doc.custom_pdf_display_exchange_rate = rate

	if not rate:
		return

	doc.custom_pdf_display_amount = flt((doc.get("base_net_total") or 0) / rate, 2)
	doc.custom_pdf_display_vat_amount = flt(
		(doc.get("base_total_taxes_and_charges") or 0) / rate, 2
	)


@frappe.whitelist()
def get_pdf_exchange_rate(company, posting_date, display_currency, company_currency=None):
	display = (display_currency or "").strip()
	if not display or not company:
		return 0

	company_ccy = company_currency or frappe.get_cached_value(
		"Company", company, "default_currency"
	)
	return lookup_pdf_exchange_rate(display, company_ccy, posting_date)


@frappe.whitelist()
def get_pdf_display_amounts(
	company,
	posting_date,
	display_currency,
	base_total,
	base_vat,
	exchange_rate=None,
	company_currency=None,
):
	display = (display_currency or "").strip()
	if not display or not company:
		return None

	company_ccy = company_currency or frappe.get_cached_value(
		"Company", company, "default_currency"
	)
	rate = flt(exchange_rate)
	if not rate:
		rate = lookup_pdf_exchange_rate(display, company_ccy, posting_date)
	if not rate:
		return {"taxable": 0, "vat": 0, "rate": 0}

	return {
		"taxable": flt(flt(base_total) / rate, 2),
		"vat": flt(flt(base_vat) / rate, 2),
		"rate": flt(rate, 9),
	}


def lookup_pdf_exchange_rate(display_ccy, company_ccy, posting_date):
	"""1 display = [?] company, e.g. 1 USD = 3.75 SAR. No throw if missing."""
	if not display_ccy or not company_ccy:
		return 0.0
	if display_ccy == company_ccy:
		return 1.0

	row = _get_exchange_row(display_ccy, company_ccy, posting_date) or _get_exchange_row(
		company_ccy, display_ccy, posting_date
	)
	if not row or not flt(row.get("exchange_rate")):
		return 0.0

	quoted = flt(row.get("exchange_rate"))
	from_ccy = row.get("from_currency")
	to_ccy = row.get("to_currency")

	# 1 display = quoted company
	if from_ccy == display_ccy and to_ccy == company_ccy:
		return quoted if quoted >= 1 else flt(1.0 / quoted, 9)

	# 1 company = quoted display (this site: SAR→USD 3.75 means 1 USD = 3.75 SAR)
	if from_ccy == company_ccy and to_ccy == display_ccy:
		return quoted if quoted >= 1 else flt(1.0 / quoted, 9)

	return quoted if quoted >= 1 else flt(1.0 / quoted, 9)


def _get_exchange_row(from_currency, to_currency, transaction_date):
	if not from_currency or not to_currency:
		return None

	filters = {"from_currency": from_currency, "to_currency": to_currency}
	date = transaction_date or nowdate()
	rows = frappe.get_all(
		"Currency Exchange",
		filters={**filters, "date": ["<=", date]},
		fields=["from_currency", "to_currency", "exchange_rate", "date"],
		order_by="date desc",
		limit=1,
	)
	if rows:
		return rows[0]

	rows = frappe.get_all(
		"Currency Exchange",
		filters=filters,
		fields=["from_currency", "to_currency", "exchange_rate", "date"],
		order_by="date desc",
		limit=1,
	)
	return rows[0] if rows else None
