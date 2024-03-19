# Copyright (c) 2024, BioTime and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import getseries


class DeviceLog(Document):
    """
    Class representing a device log.
    """

    def after_insert(self):
        """
        Method to be called after a new DeviceLog document is inserted.
        If the emp_code exists in Employee, it creates an Employee Check In.
        """
        employee = frappe.db.exists("Employee", {"attendance_device_id": self.emp_code})
        if employee and self.emp_code:
            employee_name = frappe.db.get_value("Employee", {"attendance_device_id": self.emp_code}, "name")
            log_type = "IN" if self.punch_state_display == "Check In" else "OUT"
            prefix = "EMP-CKIN-{name}-".format(name=self.name)
            series = getseries(prefix, 5)
            name = prefix + str(series)
            query = """
            INSERT INTO `tabEmployee Checkin` 
            (name, employee, log_type, time, device_id) 
            VALUES (%s, %s, %s, %s, %s)
            """
            values = (name, employee_name, log_type, self.punch_time, self.terminal_sn)

            frappe.db.sql(query, values)

            self.synced = 1
            self.employee_check_in = name

    def on_trash(self):
        """
        Method to be called when a DeviceLog document is deleted.
        If the Employee Check In exists, it deletes it.
        """
        if self.employee_check_in:
            if frappe.db.exists("Employee Checkin", self.employee_check_in):
                frappe.delete_doc("Employee Checkin", self.employee_check_in)