import frappe

MARKER = "<!-- BOT_PRINT_PDF_DISPLAY -->"
INCLUDE = '{% include "templates/includes/bot_print/pdf_foreign_amount.html" ignore missing %}'
BLOCK = f"\n{MARKER}\n{INCLUDE}\n"
SIGNATURE_HTML = (
	'<p class="bold" style="font-size: 12px;margin-top: 10%;">'
	"Authorized Signature ________________________________</p>"
)


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
	html = _strip_existing_block(doc.html or "")
	html = _place_block(html)
	if html == (doc.html or ""):
		return "already"

	doc.html = html
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return "injected"


def _strip_existing_block(html: str) -> str:
	if MARKER not in html:
		return html
	return html.replace(BLOCK, "").replace(f"{MARKER}\n{INCLUDE}", "").replace(MARKER, "").replace(INCLUDE, "")


def _place_block(html: str) -> str:
	if SIGNATURE_HTML in html:
		return html.replace(SIGNATURE_HTML, BLOCK + SIGNATURE_HTML, 1)
	return html.rstrip() + BLOCK
