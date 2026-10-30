import frappe
from frappe.tests import IntegrationTestCase

DOCTYPE = "Equipment Request"
EMPLOYEE = "ana@acme.localhost"
OTHER_EMPLOYEE = "omar@acme.localhost"
APPROVER = "priya@acme.localhost"


def ensure_user(email, roles):
	for role in roles:
		if not frappe.db.exists("Role", role):
			frappe.get_doc({"doctype": "Role", "role_name": role, "desk_access": 1}).insert()
	if not frappe.db.exists("User", email):
		frappe.get_doc(
			{"doctype": "User", "email": email, "first_name": email.split("@")[0], "send_welcome_email": 0}
		).insert()
	frappe.get_doc("User", email).add_roles(*roles)


def request(requested_by, item="Laptop", cost=1500, status="Pending"):
	return frappe.get_doc(
		{"doctype": DOCTYPE, "requested_by": requested_by, "item": item, "cost": cost, "status": status}
	).insert()


def api(name):
	return frappe.get_attr(f"acme.equipment.{name}")


class TestEquipmentApi(IntegrationTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		ensure_user(EMPLOYEE, ["Equipment User"])
		ensure_user(OTHER_EMPLOYEE, ["Equipment User"])
		ensure_user(APPROVER, ["Equipment User", "Equipment Approver"])
		frappe.db.commit()

	def setUp(self):
		frappe.set_user("Administrator")
		frappe.db.delete(DOCTYPE)

	def tearDown(self):
		frappe.set_user("Administrator")

	def test_my_requests_returns_only_own_newest_first(self):
		first = request(EMPLOYEE, item="Monitor")
		frappe.db.set_value(DOCTYPE, first.name, "creation", "2026-01-01 09:00:00")
		second = request(EMPLOYEE, item="Keyboard")
		request(OTHER_EMPLOYEE, item="Chair")

		frappe.set_user(EMPLOYEE)
		rows = api("get_my_requests")()
		self.assertEqual([r["name"] for r in rows], [second.name, first.name])
		self.assertTrue({"name", "item", "cost", "status"} <= set(rows[0]))

	def test_guests_cannot_list_requests(self):
		frappe.set_user("Guest")
		with self.assertRaises(frappe.PermissionError):
			frappe.is_whitelisted(api("get_my_requests"))

	def test_logged_in_users_can_list_requests(self):
		frappe.set_user(EMPLOYEE)
		frappe.is_whitelisted(api("get_my_requests"))

	def test_approver_approves(self):
		doc = request(EMPLOYEE)
		frappe.set_user(APPROVER)
		api("decide")(doc.name, "Approved")
		self.assertEqual(frappe.db.get_value(DOCTYPE, doc.name, ["status", "decided_by"]), ("Approved", APPROVER))

	def test_approver_rejects(self):
		doc = request(EMPLOYEE)
		frappe.set_user(APPROVER)
		api("decide")(doc.name, "Rejected")
		self.assertEqual(frappe.db.get_value(DOCTYPE, doc.name, "status"), "Rejected")

	def test_non_approver_cannot_decide(self):
		doc = request(EMPLOYEE)
		frappe.set_user(OTHER_EMPLOYEE)
		with self.assertRaises(frappe.PermissionError):
			api("decide")(doc.name, "Approved")
		self.assertEqual(frappe.db.get_value(DOCTYPE, doc.name, "status"), "Pending")

	def test_requester_cannot_decide_own_request(self):
		frappe.set_user(EMPLOYEE)
		doc = request(EMPLOYEE)
		with self.assertRaises(frappe.PermissionError):
			api("decide")(doc.name, "Approved")

	def test_approver_cannot_decide_own_request(self):
		doc = request(APPROVER)
		frappe.set_user(APPROVER)
		with self.assertRaises(frappe.PermissionError):
			api("decide")(doc.name, "Approved")
		self.assertEqual(frappe.db.get_value(DOCTYPE, doc.name, "status"), "Pending")

	def test_unknown_decision_is_rejected(self):
		doc = request(EMPLOYEE)
		frappe.set_user(APPROVER)
		with self.assertRaises(frappe.ValidationError):
			api("decide")(doc.name, "Maybe")

	def test_decided_request_cannot_be_decided_again(self):
		doc = request(EMPLOYEE, status="Rejected")
		frappe.set_user(APPROVER)
		with self.assertRaises(frappe.ValidationError):
			api("decide")(doc.name, "Approved")
		self.assertEqual(frappe.db.get_value(DOCTYPE, doc.name, "status"), "Rejected")

	def test_decide_accepts_only_post(self):
		methods = frappe.allowed_http_methods_for_whitelisted_func.get(api("decide"))
		self.assertEqual(methods, ["POST"])
