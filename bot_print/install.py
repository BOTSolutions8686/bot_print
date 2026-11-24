import frappe

MARKER = "<!-- BOT_PRINT_PDF_DISPLAY -->"
INCLUDE = (
	'{% include "templates/includes/bot_print/pdf_foreign_amount.html" ignore missing %}'
)
BLOCK = f"\n{MARKER}\n{INCLUDE}\n"


def after_migrate():
	_inject_into_multi_currency_formats()


def _inject_into_multi_currency_formats():
	if not frappe.db.exists("DocType", "Print Format"):
		return

	names = frappe.get_all(
		"Print Format",
		filters={"doc_type": "Sales Invoice", "disabled": 0},
		or_filters=[
			["name", "like", "%Multiple Currency%"],
			["name", "like", "%Multi Currency%"],
		],
		pluck="name",
	)
	for name in names:
		inject_pdf_display_block(name)


def inject_pdf_display_block(print_format_name: str) -> str:
	if not frappe.db.exists("Print Format", print_format_name):
		return "missing"

	doc = frappe.get_doc("Print Format", print_format_name)
	html = doc.html or ""
	if MARKER in html:
		return "already"

	doc.html = html.rstrip() + BLOCK
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return "injected"
