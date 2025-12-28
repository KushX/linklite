// Copyright (c) 2024, Build With Hussain and contributors
// For license information, please see license.txt

frappe.ui.form.on("Short Link", {
	refresh(frm) {
		frm.sidebar
			.add_user_action(__("Copy short link"))
			.attr("href", "#")
			.on("click", () => {
				const url = frappe.urllib.get_full_url(frm.doc.short_link);
				frappe.utils.copy_to_clipboard(url, __("Short link copied"));
			});

		frm.add_custom_button("Regenerate QR Code", () => {
			// Enable QR code checkbox and save first
			frm.set_value("enable_qr_code", 1);
			frm.save().then(() => {
				frm.call("generate_qr_code").then(() => {
					frappe.show_alert("Regenerated!")
					frm.refresh()
				})
			})
		})
	},
});
