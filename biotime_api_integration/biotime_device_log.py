import frappe
import json
import requests

def get_token():
    """
    Function to get the authentication token from the BioTime server.
    It uses the BioTime Settings to get the server IP, port, username, and password.
    It then sends a POST request to the server and returns the token from the response.
    """
    biotime_settings = frappe.get_doc("BioTime Settings")
    url = f"{biotime_settings.server_ip}:{biotime_settings.port}/api-token-auth/"
    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "username": biotime_settings.username,
        "password": biotime_settings.password,
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.json().get("non_field_errors"):
        frappe.throw(response.json().get("non_field_errors")[0])
    return response.json()["token"]

def get_response(next_url=None):
    """
    Function to get the response from the BioTime server.
    It uses the BioTime Settings to get the server IP, port, and last synced ID.
    It then sends a GET request to the server and returns the response.
    If a next_url is provided, it uses that URL for the request instead.
    """
    try:
        biotime_settings = frappe.get_doc("BioTime Settings")
        token = get_token()
        page = 1
        if biotime_settings.last_synced_id:
            page = (biotime_settings.last_synced_id // 10) + 1
        url = f"{biotime_settings.server_ip}:{biotime_settings.port}/iclock/api/transactions/?page={page}&&page_size=10"
        if next_url:
            url = next_url
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {token}",
        }
        response = requests.get(url, headers=headers)
        return response.json()
    except Exception as e:
        # insert into Sync Logs
        frappe.log_error(frappe.get_traceback(), ("Sync Error"))
        frappe.db.sql("INSERT INTO `tabSync Logs` (title, response) VALUES (%s, %s)", ("Sync Error", str(e)))

def update_employee_logs_seq(row):
    """
    Function to update the last synced ID in the BioTime Settings.
    It takes a row from the response data and sets the last synced ID to the ID of the row.
    It then saves the BioTime Settings and commits the transaction.
    """
    biotime_settings = frappe.get_doc("BioTime Settings")
    biotime_settings.last_synced_id = row["id"]
    biotime_settings.save(ignore_permissions=True)
    frappe.db.commit()
def employee_check_in_device_log():
    """
    Function to check in employee device log.
    It fetches the response from the device and updates the device log and employee logs accordingly.
    """
    response = get_response()
    next_url= response["next"]
    try:
        while next_url and response["count"] > 10:
            # my logic
            for row in response["data"]:
                if not frappe.db.exists("Device Log", row["id"]):
                    row["doctype"] = "Device Log"
                    biotime_device_log = frappe.get_doc(row)
                    biotime_device_log.save(ignore_permissions=True)
                    update_employee_logs_seq(row)
            response = get_response(next_url=next_url)
            next_url= response["next"]
        else:
            for row in response["data"]:
                if not frappe.db.exists("Device Log", row["id"]):
                    row["doctype"] = "Device Log"
                    biotime_device_log = frappe.get_doc(row)
                    biotime_device_log.save()
                    update_employee_logs_seq(row)
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), ("Sync Error"))
        frappe.db.sql("INSERT INTO `tabSync Logs` (title, response) VALUES (%s, %s)", ("Sync Error", str(e)))

