import frappe
from frappe.utils import flt
from erpnext.setup.utils import get_exchange_rate

USD_SAR_PEG = 3.75


def set_pdf_foreign_amounts(doc, method=None):
	ccy = (doc.get("custom_pdf_display_currency") or "").strip()
	if not ccy:
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
	if display_ccy == company_ccy:
		return 1.0

	rate = 0.0
	try:
		rate = flt(get_exchange_rate(display_ccy, company_ccy, posting_date))
	except Exception:
		rate = 0.0

	if display_ccy == "USD" and company_ccy == "SAR":
		if not rate or abs(rate - 1.0) < 0.0001:
			return USD_SAR_PEG

	return rate
