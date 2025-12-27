import frappe


def get_context(context):
    link = frappe.form_dict.get("link")

    if not link:
        frappe.throw("Invalid verification link", frappe.DoesNotExistError)

    if not frappe.db.exists("Short Link", link):
        frappe.throw("Link not found", frappe.DoesNotExistError)

    short_link = frappe.get_doc("Short Link", link)

    context.destination_url = short_link.destination_url
    context.redirect_url = f"/verify-redirect?link={link}&token={frappe.generate_hash(length=16)}"
    context.no_cache = 1

    return context
