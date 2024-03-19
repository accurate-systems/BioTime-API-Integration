## BioTime Integration App

## Overview
    The BioTime Integration App integrates BioTime server functionalities with ERPNext. It allows for seamless synchronization of employee logs, check-ins, and device data between BioTime and ERPNext.

## Features
    Automatic token retrieval for authentication with the BioTime server.
    Fetching employee logs and check-ins from the BioTime server and updating ERPNext accordingly.
    Updating the employee_id_on_system field in tabBioTime Device Log based on employee data from ERPNext.

## Installation
    Clone the repository to your ERPNext instance's apps directory.
    git clone https://github.com/ahmedemamhatem/BioTime-API-Integration.git
    Install the app using the bench command.
    bench --site sitename install-app biotime_integration

## Set up BioTime Settings in ERPNext.
    Navigate to BioTime Settings in ERPNext.
    Enter the server IP, port, username, and password for the BioTime server.
    Save the settings.

## Usage
    Token Retrieval
        The app automatically retrieves the authentication token from the BioTime server using the provided credentials.
        Tokens are stored securely in ERPNext for future API calls.

    Synchronization Process
        Run the employee_check_in_device_log() function to synchronize employee logs and check-ins from the BioTime server.
        The function fetches data in batches, processes it, and updates ERPNext accordingly.
        Employee logs are created in tabBioTime Device Log and Employee Checkin documents.
        The employee_id_on_system field in tabBioTime Device Log is updated based on employee data from ERPNext.

    Manual Sync and Error Handling
        In case of manual sync or error handling, refer to the functions get_token(), get_response(), update_employee_logs_seq(), update_employee_id_on_system(), and Sync Logs in ERPNext.
        Errors and sync logs are logged in tabSync Logs in ERPNext for troubleshooting and monitoring.

## User Manual
    Sync Logs
        The tabSync Logs document in ERPNext logs all sync operations, including success and error messages.
        Users can refer to tabSync Logs for sync history and error details.

    Token Management
        Tokens retrieved from the BioTime server are securely stored in ERPNext.
        Users should ensure the confidentiality and security of BioTime server credentials in BioTime Settings.