frappe.ui.form.on("Sales Invoice", {
	refresh(frm) {
		frm.set_df_property(
			"custom_pdf_display_amount",
			"description",
			__("Print only. Does not change invoice totals or ZATCA XML.")
		);
	},
});
