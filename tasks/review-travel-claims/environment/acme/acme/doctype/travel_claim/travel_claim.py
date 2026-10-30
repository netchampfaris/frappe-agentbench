import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import date_diff, flt


class TravelClaim(Document):
	def validate(self):
		self.validate_dates()
		self.total = self.get_per_diem_total()

	def validate_dates(self):
		if self.to_date < self.from_date:
			frappe.throw(_("To Date cannot be before From Date"))

	def get_per_diem_total(self):
		"""Per diem is paid for every day of the trip, counting the first and the last day."""
		days = date_diff(self.to_date, self.from_date)
		return flt(self.per_diem_rate) * days

	def on_update(self):
		if self.has_value_changed("status"):
			frappe.msgprint(f"Claim for <b>{self.purpose}</b> is now {self.status}")
			self.add_comment("Info", _("Status changed to {0}").format(self.status))
			frappe.db.commit()
