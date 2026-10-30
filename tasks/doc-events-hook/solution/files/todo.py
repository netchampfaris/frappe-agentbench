import frappe
from frappe import _


def add_closed_comment(doc, method=None):
	if not doc.reference_type or not doc.reference_name:
		return
	if doc.status != "Closed" or not doc.has_value_changed("status"):
		return

	reference = frappe.get_doc(doc.reference_type, doc.reference_name)
	reference.add_comment("Info", _("Task closed: {0}").format(doc.description))
