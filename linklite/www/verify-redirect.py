import frappe


def get_context(context):
    link = frappe.form_dict.get("link")
    token = frappe.form_dict.get("token")

    if not link or not token:
        frappe.throw("Invalid request", frappe.DoesNotExistError)

    if not frappe.db.exists("Short Link", link):
        frappe.throw("Link not found", frappe.DoesNotExistError)

    short_link = frappe.get_doc("Short Link", link)

    # Record the click
    click = frappe.new_doc("Short Link Click")
    request_headers = frappe.request.headers
    click.ip = request_headers.get("X-Real-Ip")
    click.user_agent = request_headers.get("User-Agent")
    click.referrer = request_headers.get("Referer")
    click.link = short_link.name
    click.insert().submit()
    frappe.db.commit()

    # Redirect to destination
    frappe.redirect(short_link.destination_url)
