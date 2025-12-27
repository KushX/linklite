# Copyright (c) 2024, Build With Hussain and contributors
# For license information, please see license.txt

import frappe

from frappe.model.document import Document


class ShortLink(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		description: DF.SmallText | None
		destination_url: DF.Data
		enable_qr_code: DF.Check
		expires_on: DF.Date | None
		is_disabled: DF.Check
		qr_code: DF.AttachImage | None
		require_captcha: DF.Check
		short_link: DF.Data
		skip_link_manager_role: DF.Check
	# end: auto-generated types

	def before_insert(self):
		self.validate_blacklisted_slug()
		self.validate_nested_slug()
		self.set_default_expiry()

	def set_default_expiry(self):
		if not self.expires_on:
			self.expires_on = frappe.utils.add_days(frappe.utils.today(), 30)

	def after_insert(self):
		if self.enable_qr_code:
			self.generate_qr_code()

	@frappe.whitelist()
	def generate_qr_code(self):
		import qrcode
		import io

		img = qrcode.make(f"{frappe.utils.get_url()}/{self.short_link}")
		output = io.BytesIO()
		img.save(output, format="PNG")
		hex_data = output.getvalue()

		file = frappe.get_doc({
			"doctype": "File",
			"file_name": f"qr-code-{self.name}.png",
			"content": hex_data,
			"attached_to_doctype": "Short Link",
			"attached_to_name": self.name,
			"attached_to_field": "qr_code"
		}).save()

		self.qr_code = file.file_url
		self.save()

	def validate_blacklisted_slug(self):
		if frappe.db.exists("Blacklisted Slug", self.short_link):
			frappe.throw(f"Slug {frappe.bold(self.short_link)} is not allowed!")

	def validate_nested_slug(self):
		if "/" in self.short_link:
			frappe.throw("Short link cannot contain '/'!")

	def on_trash(self):
		# delete the "Short Link Click" records
		frappe.db.delete("Short Link Click", {"link": self.name})
