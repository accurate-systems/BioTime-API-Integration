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
		self.check_connection()
		frappe.enqueue(
        method=employee_check_in_device_log,  
        queue='long',  
        timeout=7200  
   		 )

