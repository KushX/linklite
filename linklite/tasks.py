import frappe


def disable_expired_links():
	"""Disable all short links that have expired."""
	expired_links = frappe.get_all(
		"Short Link",
		filters={
			"is_disabled": 0,
			"expires_on": ["<", frappe.utils.today()]
		},
		pluck="name"
	)

	for link in expired_links:
		frappe.db.set_value("Short Link", link, "is_disabled", 1)

	if expired_links:
		frappe.db.commit()
