def show_pdf_foreign_amount(doc) -> bool:
	currency = (doc.get("custom_pdf_display_currency") or "").strip()
	amount = doc.get("custom_pdf_display_amount")
	return bool(currency and amount not in (None, "", 0, 0.0))


def pdf_foreign_currency(doc) -> str:
	return (doc.get("custom_pdf_display_currency") or "").strip()


def pdf_foreign_amount(doc) -> float:
	try:
		return float(doc.get("custom_pdf_display_amount") or 0)
	except (TypeError, ValueError):
		return 0.0
