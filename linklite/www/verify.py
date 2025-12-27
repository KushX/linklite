import hmac
import hashlib
import frappe


def generate_captcha_token(link: str) -> str:
    """Generate an HMAC token for captcha verification."""
    secret = frappe.local.conf.get("secret_key", frappe.local.conf.get("encryption_key", ""))
    message = f"captcha:{link}".encode()
    return hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()[:32]


def get_context(context):
    link = frappe.form_dict.get("link")

    if not link:
        frappe.throw("Invalid verification link", frappe.DoesNotExistError)

    if not frappe.db.exists("Short Link", link):
        frappe.throw("Link not found", frappe.DoesNotExistError)

    short_link = frappe.get_doc("Short Link", link)

    token = generate_captcha_token(link)

    context.destination_url = short_link.destination_url
    context.redirect_url = f"/verify-redirect?link={link}&token={token}"
    context.no_cache = 1

    return context
