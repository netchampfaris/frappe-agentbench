import frappe
from frappe.tests import IntegrationTestCase

DOCTYPE = "Room Booking"


def booking(room="Everest", starts_at="2026-01-05 10:00", ends_at="2026-01-05 11:00", **kwargs):
	return frappe.get_doc(
		{"doctype": DOCTYPE, "room": room, "starts_at": starts_at, "ends_at": ends_at, **kwargs}
	)


class TestRoomBooking(IntegrationTestCase):
	def setUp(self):
		frappe.db.delete(DOCTYPE)

	def test_doctype_shape(self):
		meta = frappe.get_meta(DOCTYPE)
		self.assertEqual(meta.module, "Acme")
		fields = {f.fieldname: f for f in meta.fields}
		for name, fieldtype in (("room", "Data"), ("starts_at", "Datetime"), ("ends_at", "Datetime"), ("attendees", "Int")):
			self.assertEqual(fields[name].fieldtype, fieldtype, name)
		for name in ("room", "starts_at", "ends_at"):
			self.assertTrue(fields[name].reqd, f"{name} should be required")

	def test_valid_booking_saves(self):
		doc = booking(attendees=4).insert()
		self.assertTrue(frappe.db.exists(DOCTYPE, doc.name))

	def test_missing_room_is_rejected(self):
		with self.assertRaises(frappe.MandatoryError):
			booking(room=None).insert()

	def test_end_before_start_is_rejected(self):
		with self.assertRaises(frappe.ValidationError):
			booking(starts_at="2026-01-05 11:00", ends_at="2026-01-05 10:00").insert()

	def test_zero_length_is_rejected(self):
		with self.assertRaises(frappe.ValidationError):
			booking(starts_at="2026-01-05 10:00", ends_at="2026-01-05 10:00").insert()

	def test_partial_overlap_is_rejected(self):
		booking().insert()
		with self.assertRaises(frappe.ValidationError):
			booking(starts_at="2026-01-05 10:30", ends_at="2026-01-05 11:30").insert()

	def test_booking_inside_another_is_rejected(self):
		booking(starts_at="2026-01-05 09:00", ends_at="2026-01-05 12:00").insert()
		with self.assertRaises(frappe.ValidationError):
			booking(starts_at="2026-01-05 10:00", ends_at="2026-01-05 10:15").insert()

	def test_booking_around_another_is_rejected(self):
		booking(starts_at="2026-01-05 10:00", ends_at="2026-01-05 10:15").insert()
		with self.assertRaises(frappe.ValidationError):
			booking(starts_at="2026-01-05 09:00", ends_at="2026-01-05 12:00").insert()

	def test_touching_bookings_are_allowed(self):
		booking().insert()
		booking(starts_at="2026-01-05 11:00", ends_at="2026-01-05 12:00").insert()
		booking(starts_at="2026-01-05 09:00", ends_at="2026-01-05 10:00").insert()

	def test_other_rooms_do_not_conflict(self):
		booking().insert()
		booking(room="Kilimanjaro").insert()

	def test_saving_existing_booking_does_not_conflict_with_itself(self):
		doc = booking().insert()
		doc.attendees = 8
		doc.save()

	def test_moving_a_booking_into_a_clash_is_rejected(self):
		booking().insert()
		other = booking(starts_at="2026-01-05 12:00", ends_at="2026-01-05 13:00").insert()
		other.starts_at = "2026-01-05 10:30"
		with self.assertRaises(frappe.ValidationError):
			other.save()
