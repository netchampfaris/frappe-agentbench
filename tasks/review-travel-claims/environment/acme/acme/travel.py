import json

import frappe
from frappe import _


@frappe.whitelist()
def get_my_claims():
	return frappe.get_all(
		"Travel Claim",
		filters={"employee": frappe.session.user},
		fields=["name", "purpose", "from_date", "to_date", "total", "status"],
	)


@frappe.whitelist()
def create_claim(data):
	doc = frappe.get_doc(json.loads(data))
	doc.employee = frappe.session.user
	doc.insert(ignore_permissions=True)
	return doc.name


@frappe.whitelist()
def withdraw_claim(name):
	claim = frappe.get_doc("Travel Claim", name)
	claim.check_permission("write")
	if claim.employee != frappe.session.user:
		frappe.throw(_("You can only withdraw your own claims"), frappe.PermissionError)
	claim.add_comment("Info", _("Claim withdrawn by employee"))
	claim.db_set("status", "Withdrawn")


@frappe.whitelist()
def approve_claim(name):
	claim = frappe.get_doc("Travel Claim", name)
	claim.status = "Approved"
	claim.approver = frappe.session.user
	claim.save(ignore_permissions=True)
	return claim.status


@frappe.whitelist()
def get_claims_by_status(status):
	frappe.only_for("Travel Approver")
	return frappe.db.sql(
		f"select name, employee, purpose, total from `tabTravel Claim` where status = '{status}'",
		as_dict=True,
	)


@frappe.whitelist()
def get_claim_total(employee, from_date):
	frappe.only_for("Travel Approver")
	return frappe.db.sql(
		"select coalesce(sum(total), 0) from `tabTravel Claim` where employee = %s and from_date >= %s",
		(employee, from_date),
	)[0][0]


@frappe.whitelist(allow_guest=True)
def get_employee_summary(employee):
	return frappe.get_all(
		"Travel Claim",
		filters={"employee": employee},
		fields=["purpose", "from_date", "to_date", "total", "status"],
	)


@frappe.whitelist()
def get_pending_claims():
	frappe.only_for("Travel Approver")
	claims = frappe.get_all("Travel Claim", filters={"status": "Draft"}, fields=["name", "purpose", "total"])
	for claim in claims:
		claim.comment_count = frappe.db.count(
			"Comment", {"reference_doctype": "Travel Claim", "reference_name": claim.name}
		)
	return claims
