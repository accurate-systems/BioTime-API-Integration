import frappe
from frappe.model.document import Document
from frappe.model.naming import getseries


class BioTimeDeviceLog(Document):
	"""
	Class representing a BioTime Device Log.
	"""

	def after_insert(self):
		"""
		Method to be called after a new BioTimeDeviceLog document is inserted.
		If the emp_code exists in Employee, it creates an Employee Check In using SQL INSERT.
		"""
		employee_id = frappe.db.get_value("Employee", {"attendance_device_id": self.emp_code}, "name")
		if employee_id and self.emp_code:
			log_type = "IN" if self.punch_state_display == "Check In" else "OUT"
			prefix = "EMP-CKIN-{name}-".format(name=self.name)
			series = frappe.db.get_value("tabSeries", {"name": prefix}, "current") or 0
			name = prefix + str(series + 1)

			# Insert Employee Checkin using SQL
			query = """
			INSERT INTO `tabEmployee Checkin` 
			(name, employee, log_type, time, device_id, punch_type, creation, modified, modified_by, owner) 
			VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
			"""
			values = (name, employee_id, log_type, self.punch_time, self.terminal_sn, "Device Punch", self.creation, self.modified, "Administrator", "Administrator")
			frappe.db.sql(query, values)

			# Update BioTimeDeviceLog fields using SQL update
			update_query = """
			UPDATE `tabBioTime Device Log`
			SET synced = 1, employee_check_in = %s
			WHERE name = %s
			"""
			update_values = (name, self.name)
			frappe.db.sql(update_query, update_values)



	def on_trash(self):
		"""
		Method to be called when a BioTimeDeviceLog document is deleted.
		If the Employee Check In exists, it deletes it.
		"""
		if self.employee_check_in:
			if frappe.db.exists("Employee Checkin", self.employee_check_in):
				# sql query to delete the Employee Checkin
				query = f"""
				DELETE FROM `tabEmployee Checkin` WHERE name = %s
				"""
				values = (self.employee_check_in,)

				frappe.db.sql(query, values)