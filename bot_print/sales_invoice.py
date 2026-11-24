import frappe
from frappe.utils import flt, nowdate

USD_SAR_PEG = 3.75


def set_pdf_foreign_amounts(doc, method=None):
	ccy = (doc.get("custom_pdf_display_currency") or "").strip()
	if not ccy:
		return

	# Keep figures the client already typed. Fill only when empty / 0.
	if flt(doc.get("custom_pdf_display_amount")) or flt(doc.get("custom_pdf_display_vat_amount")):
		return

	amounts = calculate_pdf_display_amounts(
		doc.get("company"),
		doc.get("posting_date"),
		ccy,
		doc.get("base_total") or 0,
		doc.get("base_total_taxes_and_charges") or 0,
		doc.get("company_currency"),
	)
	if not amounts:
		return

	doc.custom_pdf_display_amount = amounts["taxable"]
	doc.custom_pdf_display_vat_amount = amounts["vat"]


@frappe.whitelist()
def get_pdf_display_amounts(company, posting_date, display_currency, base_total, base_vat):
	return calculate_pdf_display_amounts(
		company, posting_date, display_currency, base_total, base_vat
	)


def calculate_pdf_display_amounts(
	company, posting_date, display_currency, base_total, base_vat, company_currency=None
):
	display = (display_currency or "").strip()
	if not display or not company:
		return None

	company_ccy = company_currency or frappe.get_cached_value(
		"Company", company, "default_currency"
	)
	taxable = flt(base_total)
	vat = flt(base_vat)
	rate = _company_per_display_rate(display, company_ccy, posting_date)
	if not rate:
		return None

	return {
		"taxable": flt(taxable / rate, 2),
		"vat": flt(vat / rate, 2),
		"rate": flt(rate, 6),
	}


def _company_per_display_rate(display_ccy, company_ccy, posting_date):
	"""SAR per 1 USD so PDF USD = SAR / rate. Uses Currency Exchange if present."""
	if display_ccy == company_ccy:
		return 1.0

	row = _get_exchange_row(display_ccy, company_ccy, posting_date) or _get_exchange_row(
		company_ccy, display_ccy, posting_date
	)
	if row and flt(row.get("exchange_rate")):
		quoted = flt(row.get("exchange_rate"))
		# This site stores SAR→USD as 3.75 (peg). Use 3.75 as SAR per 1 USD.
		# A correct 1 SAR = 0.2667 USD is inverted to the same peg.
		if quoted >= 1:
			return quoted
		return flt(1.0 / quoted, 9)

	if display_ccy == "USD" and company_ccy == "SAR":
		return USD_SAR_PEG
	if display_ccy == "SAR" and company_ccy == "USD":
		return flt(1.0 / USD_SAR_PEG, 9)

	return 0.0


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
