import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_datetime


class RoomBooking(Document):
	def validate(self):
		if get_datetime(self.ends_at) <= get_datetime(self.starts_at):
			frappe.throw(_("End time must be later than start time"))

		clash = frappe.db.exists(
			"Room Booking",
			{
				"room": self.room,
				"name": ("!=", self.name or ""),
				"starts_at": ("<", self.ends_at),
				"ends_at": (">", self.starts_at),
			},
		)
		if clash:
			frappe.throw(_("{0} is already booked at this time ({1})").format(self.room, clash))
