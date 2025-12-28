import hmac
import hashlib
import frappe

# Allow guests to access this page (for QR code scans)
allow_guest = True


def verify_captcha_token(link: str, token: str) -> bool:
    """Verify the HMAC token for captcha verification using constant-time comparison."""
    secret = frappe.local.conf.get("secret_key", frappe.local.conf.get("encryption_key", ""))
    message = f"captcha:{link}".encode()
    expected_token = hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()[:32]
    return hmac.compare_digest(expected_token, token)


def get_context(context):
    link = frappe.form_dict.get("link")
    token = frappe.form_dict.get("token")

    if not link or not token:
        frappe.throw("Invalid request", frappe.DoesNotExistError)

    if not frappe.db.exists("Short Link", link):
        frappe.throw("Link not found", frappe.DoesNotExistError)

    # Validate the captcha token
    if not verify_captcha_token(link, token):
        frappe.throw("Invalid verification token", frappe.DoesNotExistError)

    short_link = frappe.get_doc("Short Link", link)

    # Record the click (ignore permissions for guest access)
    click = frappe.new_doc("Short Link Click")
    request_headers = frappe.request.headers
    click.ip = request_headers.get("X-Real-Ip")
    click.user_agent = request_headers.get("User-Agent")
    click.referrer = request_headers.get("Referer")
    click.link = short_link.name
    click.insert(ignore_permissions=True).submit()
    frappe.db.commit()

    # Redirect to destination (raise Redirect to stop template rendering)
    frappe.local.flags.redirect_location = short_link.destination_url
    raise frappe.Redirect
