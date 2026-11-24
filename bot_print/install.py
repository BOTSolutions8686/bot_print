import frappe
from frappe.utils import flt, nowdate

INCLUDE_MARKER = "<!-- BOT_PRINT_PDF_DISPLAY -->"
INCLUDE = '{% include "templates/includes/bot_print/pdf_foreign_amount.html" ignore missing %}'
TAX_MARKER = "<!-- BOT_PRINT_TAX_ROWS -->"

ORIGINAL_TAX_ROWS = """    <tr>
        <td colspan="7" class="inc_size text-right bold">بيانات الضريبة المضافة بالريال</td>
    </tr>
    <tr>
        <td colspan="2"></td>
        <td colspan="2" class="inc_size text-right bold" style="color: black !important;">القيمة الخاضعة للضريبة بالريال</td>
        <td colspan="2" class="inc_size text-center bold">ريال</td>
        <td class="inc_size text-right bold" style="color: black !important;">{{ "{:,.2f}".format(doc.base_total or 0) }}</td>
    </tr>
    <tr>
        <td colspan="2"></td>
        <td colspan="2"  style="color: black !important;">القيمة قيمة الضريبة المضافة بالريال%15</td>
        <td colspan="2" class="inc_size text-center bold">ريال</td>
        <td class="inc_size text-right bold" style="color: black !important;">{{ "{:,.2f}".format(doc.base_total_taxes_and_charges or 0) }}</td>
    </tr>"""

REPLACEMENT_TAX_ROWS = """    """ + TAX_MARKER + """
    {% set pdf_ccy = (doc.get('custom_pdf_display_currency') or '')|trim %}
    {% set pdf_taxable = doc.get('custom_pdf_display_amount') %}
    {% set pdf_vat = doc.get('custom_pdf_display_vat_amount') %}
    {% set show_pdf_ccy = pdf_ccy and (pdf_taxable or pdf_vat) %}
    <tr>
        <td colspan="7" class="inc_size text-right bold">
            {%- if show_pdf_ccy -%}
                بيانات الضريبة المضافة بعملة {{ pdf_ccy }}
            {%- else -%}
                بيانات الضريبة المضافة بالريال
            {%- endif -%}
        </td>
    </tr>
    <tr>
        <td colspan="2"></td>
        <td colspan="2" class="inc_size text-right bold" style="color: black !important;">
            {%- if show_pdf_ccy -%}
                القيمة الخاضعة للضريبة ({{ pdf_ccy }})
            {%- else -%}
                القيمة الخاضعة للضريبة بالريال
            {%- endif -%}
        </td>
        <td colspan="2" class="inc_size text-center bold">
            {%- if show_pdf_ccy -%}{{ pdf_ccy }}{%- else -%}ريال{%- endif -%}
        </td>
        <td class="inc_size text-right bold" style="color: black !important;">
            {%- if show_pdf_ccy and pdf_taxable -%}
                {{ "{:,.2f}".format(pdf_taxable|float) }}
            {%- else -%}
                {{ "{:,.2f}".format(doc.base_total or 0) }}
            {%- endif -%}
        </td>
    </tr>
    <tr>
        <td colspan="2"></td>
        <td colspan="2" style="color: black !important;">
            {%- if show_pdf_ccy -%}
                القيمة قيمة الضريبة المضافة ({{ pdf_ccy }}) %15
            {%- else -%}
                القيمة قيمة الضريبة المضافة بالريال%15
            {%- endif -%}
        </td>
        <td colspan="2" class="inc_size text-center bold">
            {%- if show_pdf_ccy -%}{{ pdf_ccy }}{%- else -%}ريال{%- endif -%}
        </td>
        <td class="inc_size text-right bold" style="color: black !important;">
            {%- if show_pdf_ccy and pdf_vat -%}
                {{ "{:,.2f}".format(pdf_vat|float) }}
            {%- else -%}
                {{ "{:,.2f}".format(doc.base_total_taxes_and_charges or 0) }}
            {%- endif -%}
        </td>
    </tr>"""


def after_migrate():
	_ensure_pdf_section_collapsible()
	_ensure_usd_sar_currency_exchange()
	_patch_multi_currency_formats()


def _ensure_pdf_section_collapsible():
	name = "Sales Invoice-custom_pdf_display_section"
	if frappe.db.exists("Custom Field", name):
		frappe.db.set_value("Custom Field", name, "collapsible", 1, update_modified=False)


def _ensure_usd_sar_currency_exchange():
	"""ERPNext looks up USD→SAR (Price List). Site only had SAR→USD 3.75, so it threw."""
	if not frappe.db.exists("DocType", "Currency Exchange"):
		return

	today = nowdate()
	if frappe.db.exists(
		"Currency Exchange",
		{"from_currency": "USD", "to_currency": "SAR", "date": today},
	):
		return

	src = frappe.get_all(
		"Currency Exchange",
		filters={"from_currency": "SAR", "to_currency": "USD"},
		fields=["exchange_rate"],
		order_by="date desc",
		limit=1,
	)
	quoted = flt(src[0].exchange_rate) if src else 3.75
	rate = quoted if quoted >= 1 else flt(1.0 / quoted, 9)
	if not rate:
		rate = 3.75

	doc = frappe.get_doc(
		{
			"doctype": "Currency Exchange",
			"date": today,
			"from_currency": "USD",
			"to_currency": "SAR",
			"exchange_rate": rate,
			"for_buying": 1,
			"for_selling": 1,
		}
	)
	doc.insert(ignore_permissions=True)
	frappe.db.commit()


def _patch_multi_currency_formats():
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
	html = _strip_old_include(doc.html or "")
	updated = _replace_tax_rows(html)
	if updated == (doc.html or ""):
		return "already"

	doc.html = updated
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return "patched"


def _strip_old_include(html: str) -> str:
	html = html.replace(f"\n{INCLUDE_MARKER}\n{INCLUDE}\n", "")
	html = html.replace(f"{INCLUDE_MARKER}\n{INCLUDE}", "")
	html = html.replace(INCLUDE_MARKER, "")
	html = html.replace(INCLUDE, "")
	return html


def _replace_tax_rows(html: str) -> str:
	if TAX_MARKER in html:
		return html
	if ORIGINAL_TAX_ROWS in html:
		return html.replace(ORIGINAL_TAX_ROWS, REPLACEMENT_TAX_ROWS, 1)
	return html
