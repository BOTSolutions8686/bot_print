app_name = "bot_print"
app_title = "BOT Print"
app_publisher = "BOT Solutions"
app_description = "Reusable print extras for BOT Solutions ERPNext sites"
app_email = "info@botsolutions.tech"
app_license = "mit"

required_apps = ["frappe", "erpnext"]

fixtures = [
	{
		"dt": "Custom Field",
		"filters": [
			[
				"name",
				"in",
				[
					"Sales Invoice-custom_pdf_display_section",
					"Sales Invoice-custom_pdf_display_currency",
					"Sales Invoice-custom_pdf_display_amount",
				],
			]
		],
	},
]

after_migrate = ["bot_print.install.after_migrate"]

doctype_js = {
	"Sales Invoice": "public/js/sales_invoice.js",
}

jinja = {
	"methods": [
		"bot_print.jinja.show_pdf_foreign_amount",
		"bot_print.jinja.pdf_foreign_currency",
		"bot_print.jinja.pdf_foreign_amount",
	]
}
