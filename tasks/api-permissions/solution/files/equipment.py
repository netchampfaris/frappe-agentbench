import frappe
from frappe import _

DECISIONS = ("Approved", "Rejected")


@frappe.whitelist()
def get_my_requests():
	return frappe.get_list(
		"Equipment Request",
		filters={"requested_by": frappe.session.user},
		fields=["name", "item", "cost", "status"],
		order_by="creation desc",
	)


@frappe.whitelist(methods=["POST"])
def decide(name: str, decision: str):
	frappe.only_for("Equipment Approver")
	if decision not in DECISIONS:
		frappe.throw(_("Decision must be Approved or Rejected"))

	doc = frappe.get_doc("Equipment Request", name)
	doc.check_permission("write")
	if doc.requested_by == frappe.session.user:
		frappe.throw(_("You cannot decide your own request"), frappe.PermissionError)
	if doc.status != "Pending":
		frappe.throw(_("Only pending requests can be decided"))

	doc.status = decision
	doc.decided_by = frappe.session.user
	doc.save()
