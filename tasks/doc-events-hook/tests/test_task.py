import frappe
from frappe.tests import IntegrationTestCase


def make_note(title="Quarterly plan"):
	return frappe.get_doc({"doctype": "Note", "title": title, "content": "Plan"}).insert()


def make_todo(description="Call the vendor", reference=None):
	values = {"doctype": "ToDo", "description": description, "allocated_to": "Administrator"}
	if reference:
		values.update(reference_type=reference.doctype, reference_name=reference.name)
	return frappe.get_doc(values).insert()


def closed_comments(doc):
	return frappe.get_all(
		"Comment",
		filters={"reference_doctype": doc.doctype, "reference_name": doc.name, "comment_type": "Info"},
		pluck="content",
	)


def set_status(todo, status):
	todo.reload()
	todo.status = status
	todo.save()


class TestCloseToDoComment(IntegrationTestCase):
	def test_closing_adds_comment_on_reference(self):
		note = make_note()
		todo = make_todo("Call the vendor", note)
		self.assertEqual(closed_comments(note), [])
		set_status(todo, "Closed")
		comments = closed_comments(note)
		self.assertEqual(len(comments), 1)
		self.assertTrue(comments[0].startswith("Task closed: "), comments[0])
		self.assertIn("Call the vendor", comments[0])

	def test_saving_closed_todo_again_adds_nothing(self):
		note = make_note()
		todo = make_todo(reference=note)
		set_status(todo, "Closed")
		todo.reload()
		todo.priority = "High"
		todo.save()
		self.assertEqual(len(closed_comments(note)), 1)

	def test_reopen_and_close_adds_second_comment(self):
		note = make_note()
		todo = make_todo(reference=note)
		set_status(todo, "Closed")
		set_status(todo, "Open")
		set_status(todo, "Closed")
		self.assertEqual(len(closed_comments(note)), 2)

	# The tests below check that something does not happen. Each one ends by
	# closing a referenced ToDo, so an app that does nothing cannot pass them.

	def test_cancelling_adds_nothing(self):
		note = make_note()
		todo = make_todo(reference=note)
		set_status(todo, "Cancelled")
		self.assertEqual(closed_comments(note), [])
		set_status(todo, "Closed")
		self.assertEqual(len(closed_comments(note)), 1)

	def test_todo_without_reference_closes_cleanly(self):
		todo = make_todo()
		set_status(todo, "Closed")
		self.assertEqual(frappe.db.get_value("ToDo", todo.name, "status"), "Closed")
		note = make_note()
		set_status(make_todo(reference=note), "Closed")
		self.assertEqual(len(closed_comments(note)), 1)

	def test_other_edits_add_nothing(self):
		note = make_note()
		todo = make_todo(reference=note)
		todo.reload()
		todo.priority = "Low"
		todo.save()
		self.assertEqual(closed_comments(note), [])
		set_status(todo, "Closed")
		self.assertEqual(len(closed_comments(note)), 1)
