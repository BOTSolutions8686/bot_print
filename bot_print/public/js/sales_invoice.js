frappe.ui.form.on("Sales Invoice", {
	refresh(frm) {
		frm.set_df_property(
			"custom_pdf_display_amount",
			"description",
			__("Print only. Auto-filled from SAR totals using the display currency rate. Does not change invoice totals or ZATCA XML.")
		);
		set_pdf_foreign_amounts(frm);
	},
	custom_pdf_display_currency(frm) {
		set_pdf_foreign_amounts(frm, true);
	},
	posting_date(frm) {
		set_pdf_foreign_amounts(frm);
	},
	base_total(frm) {
		set_pdf_foreign_amounts(frm);
	},
	base_net_total(frm) {
		set_pdf_foreign_amounts(frm);
	},
	base_total_taxes_and_charges(frm) {
		set_pdf_foreign_amounts(frm);
	},
	taxes_and_charges(frm) {
		set_pdf_foreign_amounts(frm);
	},
});

let _pdf_amt_timer;

function set_pdf_foreign_amounts(frm, force) {
	const ccy = (frm.doc.custom_pdf_display_currency || "").trim();
	if (!ccy || !frm.doc.company) {
		return;
	}

	const has_amounts =
		flt(frm.doc.custom_pdf_display_amount) || flt(frm.doc.custom_pdf_display_vat_amount);
	if (!force && has_amounts) {
		return;
	}

	clearTimeout(_pdf_amt_timer);
	_pdf_amt_timer = setTimeout(() => {
		frappe.call({
			method: "bot_print.sales_invoice.get_pdf_display_amounts",
			args: {
				company: frm.doc.company,
				posting_date: frm.doc.posting_date,
				display_currency: ccy,
				base_total: frm.doc.base_total || 0,
				base_vat: frm.doc.base_total_taxes_and_charges || 0,
			},
			callback(r) {
				if (!r.message) {
					return;
				}
				if (flt(frm.doc.custom_pdf_display_amount) !== flt(r.message.taxable)) {
					frm.set_value("custom_pdf_display_amount", r.message.taxable);
				}
				if (flt(frm.doc.custom_pdf_display_vat_amount) !== flt(r.message.vat)) {
					frm.set_value("custom_pdf_display_vat_amount", r.message.vat);
				}
			},
		});
	}, 300);
}
