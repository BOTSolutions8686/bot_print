frappe.ui.form.on("Sales Invoice", {
	refresh(frm) {
		set_pdf_rate_label(frm);
		fetch_pdf_rate_if_empty(frm);
	},
	custom_pdf_display_currency(frm) {
		set_pdf_rate_label(frm);
		fetch_pdf_rate_if_empty(frm, true);
	},
	custom_pdf_display_exchange_rate(frm) {
		apply_pdf_amounts_from_rate(frm);
	},
	base_total(frm) {
		apply_pdf_amounts_from_rate(frm);
	},
	base_net_total(frm) {
		apply_pdf_amounts_from_rate(frm);
	},
	discount_amount(frm) {
		apply_pdf_amounts_from_rate(frm);
	},
	base_total_taxes_and_charges(frm) {
		apply_pdf_amounts_from_rate(frm);
	},
});

let _pdf_rate_timer;

function set_pdf_rate_label(frm) {
	const from_ccy = frm.doc.custom_pdf_display_currency || "USD";
	const to_ccy = frm.doc.currency || frm.doc.company_currency || "SAR";
	frm.set_df_property(
		"custom_pdf_display_exchange_rate",
		"description",
		__("1 {0} = [?] {1}. From Currency Exchange if present; you can type freely.", [
			from_ccy,
			to_ccy,
		])
	);
}

function apply_pdf_amounts_from_rate(frm) {
	const display = (frm.doc.custom_pdf_display_currency || "").trim();
	if (!display) {
		return;
	}
	const company = frm.doc.company_currency || "SAR";
	const net_sar = flt(frm.doc.base_net_total);
	const vat_sar = flt(frm.doc.base_total_taxes_and_charges);
	let taxable;
	let vat;
	if (display === company) {
		taxable = flt(net_sar, 2);
		vat = flt(vat_sar, 2);
	} else {
		const rate = flt(frm.doc.custom_pdf_display_exchange_rate);
		if (!rate) {
			return;
		}
		taxable = flt(net_sar / rate, 2);
		vat = flt(vat_sar / rate, 2);
	}
	if (flt(frm.doc.custom_pdf_display_amount) !== taxable) {
		frm.set_value("custom_pdf_display_amount", taxable);
	}
	if (flt(frm.doc.custom_pdf_display_vat_amount) !== vat) {
		frm.set_value("custom_pdf_display_vat_amount", vat);
	}
}

function fetch_pdf_rate_if_empty(frm, force) {
	const ccy = (frm.doc.custom_pdf_display_currency || "").trim();
	if (!ccy || !frm.doc.company) {
		return;
	}
	if (!force && flt(frm.doc.custom_pdf_display_exchange_rate)) {
		apply_pdf_amounts_from_rate(frm);
		return;
	}

	clearTimeout(_pdf_rate_timer);
	_pdf_rate_timer = setTimeout(() => {
		frappe.call({
			method: "bot_print.sales_invoice.get_pdf_exchange_rate",
			args: {
				company: frm.doc.company,
				posting_date: frm.doc.posting_date,
				display_currency: ccy,
				company_currency: frm.doc.company_currency,
			},
			callback(r) {
				const rate = flt(r.message);
				if (rate) {
					frm.set_value("custom_pdf_display_exchange_rate", rate);
				}
				apply_pdf_amounts_from_rate(frm);
			},
		});
	}, 300);
}
