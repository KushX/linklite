import frappe
from frappe.website.path_resolver import resolve_path as original_resolve_path


def path_resolver(path: str):
	# TODO: not handling "/gin?q=abc"
	if frappe.db.exists("Short Link", {"short_link": path}):
		short_link = frappe.db.get_value(
			"Short Link",
			{"short_link": path},
			["destination_url", "name", "require_captcha", "expires_on", "is_disabled"],
			as_dict=True
		)

		# Check if link is disabled or expired
		if short_link.is_disabled:
			frappe.throw("This link has been disabled", frappe.DoesNotExistError)

		if short_link.expires_on and frappe.utils.getdate(short_link.expires_on) < frappe.utils.getdate():
			frappe.throw("This link has expired", frappe.DoesNotExistError)

		# If captcha is required, redirect to verification page
		if short_link.require_captcha:
			frappe.redirect(f"/verify?link={short_link.name}")

		# Record the click
		click = frappe.new_doc("Short Link Click")

		request_headers = frappe.request.headers
		click.ip = request_headers.get("X-Real-Ip")
		click.user_agent = request_headers.get("User-Agent")
		click.referrer = request_headers.get("Referer")

		click.link = short_link.name
		click.insert().submit()
		frappe.db.commit() # to remove once MyISAM

		frappe.redirect(short_link.destination_url)

	# else pass it on!
	return original_resolve_path(path)
