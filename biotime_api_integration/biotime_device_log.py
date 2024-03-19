import frappe
import json
import requests
from frappe.utils import now_datetime


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
        frappe.db.sql("INSERT INTO `tabSync Logs` (name, title, response, creation, modified) VALUES (%s, %s, %s, NOW(), NOW())", 
                    (frappe.generate_hash("", 10), "Sync Error", str(e)))
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
    Function to check in employee BioTime Device Log.
    It fetches the response from the device and updates the BioTime Device Log and employee logs accordingly.
    """
    response = get_response()
    next_url= response["next"]
    try:
        formatted_data = ""  
        response_list = []  

        while next_url and response["count"] > 10:
            for row in response["data"]:
                if not frappe.db.exists("BioTime Device Log", row["id"]):
                    row["doctype"] = "BioTime Device Log"
                    biotime_device_log = frappe.get_doc(row)
                    biotime_device_log.save(ignore_permissions=True)
                    update_employee_logs_seq(row)
                    response_list.append(row)  # Append row to response_list
            response = get_response(next_url=next_url)
            next_url = response["next"]
        else:
            for row in response["data"]:
                if not frappe.db.exists("BioTime Device Log", row["id"]):
                    row["doctype"] = "BioTime Device Log"
                    biotime_device_log = frappe.get_doc(row)
                    biotime_device_log.save()
                    update_employee_logs_seq(row)
                    response_list.append(row)  # Append row to response_list

        update_employee_id_on_system()

        # Accumulate the data into formatted_data variable
        for item in response_list:
            formatted_data += f"ID: {item['id']}, Emp Code: {item['emp_code']}, Punch Time: {item['punch_time']}, Punch State: {item['punch_state_display']}\n\n"

        # insert into Sync Logs success
        frappe.db.sql("INSERT INTO `tabSync Logs` (name, title, response, creation, modified) VALUES (%s, %s, %s, NOW(), NOW())", 
              (frappe.generate_hash("", 10), "Sync Success", formatted_data))
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), ("Sync Error"))
        frappe.db.sql("INSERT INTO `tabSync Logs` (name, title, response, creation, modified) VALUES (%s, %s, %s, NOW(), NOW())", 
                    (frappe.generate_hash("", 10), "Sync Error", str(e)))

def update_employee_id_on_system():
    # SQL query to update employee_id_on_system in tabBioTime Device Log
    sql_query = """
        UPDATE `tabBioTime Device Log` AS log
        JOIN `tabEmployee` AS emp ON emp.attendance_device_id = log.emp_code
        SET log.employee_id_on_system = emp.name
    """
    # Execute the SQL query
    frappe.db.sql(sql_query)

    # Commit the transaction
    frappe.db.commit()