# Copyright (c) 2024, BioTime and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import requests
import json
from biotime_api_integration.biotime_device_log import employee_check_in_device_log

import frappe
import json
import requests

class BioTimeSettings(Document):
	
	@frappe.whitelist()
	def check_connection(self):
		"""
		Method to check the connection to the BioTime server.
		It uses the BioTime Settings to get the server IP, port, username, and password.
		It then sends a POST request to the server and returns the response.
		"""
		url = f"{self.server_ip}:{self.port}/api-token-auth/"
		headers = {
			"Content-Type": "application/json",
		}
		data = {
			"username": self.username,
			"password": self.password,
		}
		response = requests.post(url, headers=headers, data=json.dumps(data))
		if response.json().get("non_field_errors"):
			frappe.throw(response.json().get("non_field_errors")[0])
		return response.json()
	

	
	@frappe.whitelist()
	def sync_transactions(self):
		"""
		Enqueue the employee_check_in_device_log function as a background job.
		This function will run the check in the background without blocking the main process.
		"""
		try:
			self.check_connection()  # Ensure connection is checked before syncing
			frappe.enqueue(
				'biotime_api_integration.biotime_device_log.employee_check_in_device_log',
				queue='long',
				job_name='Employee Check In Device Log Job',
				timeout=7200
			)
			print("Job enqueued successfully.")
			return {"status": "success"}
		except Exception as e:
			frappe.log_error(frappe.get_traceback(), "Enqueue Job Error")
			error_message = str(e)
			frappe.db.sql(
				"INSERT INTO `tabSync Logs` (name, title, response, creation, modified) "
				"VALUES (%s, %s, %s, NOW(), NOW())",
				(frappe.generate_hash("", 10), "Enqueue Job Error", error_message)
			)
			print(error_message)
			# Return the error message for better client-side error handling
			return {"status": "failed", "error": error_message}
