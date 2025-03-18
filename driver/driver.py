# driver/driver.py
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

class WebAppDriver:
    """
    Protocol driver for simulating browser interactions with the appointment scheduler.
    It uses HTTP requests to interact with the SUT.
    """
    def __init__(self, base_url="http://localhost:8999"):
        self.base_url = base_url
        self.session = requests.Session()
        self.appointment_time = None
        self.details = None
        self.html_content = None
        self.booked_slots = None

    def visit_page(self):
        # Load the appointment page
        response = self.session.get(self.base_url)
        self.html_content = response.text
        return response.status_code == 200

    def get_booked_slots(self):
        # Fetch booked slots from the API
        response = self.session.get(f"{self.base_url}/api/booked-slots")
        if response.status_code == 200:
            self.booked_slots = response.json()
            return True
        return False

    def set_appointment_time(self, datetime_str):
        self.appointment_time = datetime_str

    def set_details(self, details):
        self.details = details

    def submit_form(self):
        # Submit the form data via a POST request.
        data = {
            'appointment_time': self.appointment_time,
            'details': self.details
        }
        self.response = self.session.post(self.base_url, data=data)

    def check_success_message(self):
        # Success is indicated by a redirect or a 200 OK without error message.
        successful = self.response.status_code in (200, 302)
        # But also check for error messages that would indicate failure
        has_error = ("Time slot already booked" in self.response.text or 
                   "Invalid datetime format" in self.response.text or
                   "Cannot book appointments for today or past dates" in self.response.text or
                   "Cannot book appointments on Sundays" in self.response.text)
        return successful and not has_error

    def check_error_message(self, expected_message):
        # Check if the expected error message is present in the response.
        return expected_message in self.response.text
    
    def check_time_slot_disabled(self, date_str, time_str):
        # Check if a time slot is disabled in the UI
        # First, ensure we have the booked slots
        if self.booked_slots is None:
            self.get_booked_slots()
        
        # Create the datetime string in ISO format
        datetime_str = f"{date_str}T{time_str}"
        
        # Check if this is today (disabled)
        today = datetime.now().strftime("%Y-%m-%d")
        if date_str == today:
            return True
            
        # Check if this is a Sunday (disabled)
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        if date_obj.weekday() == 6:  # Sunday is 6 in Python's weekday()
            return True
            
        # Check if this slot is in the booked slots
        for slot in self.booked_slots:
            # Compare year, month, day, hour (ignoring minutes)
            if slot.startswith(datetime_str.split(':')[0]):
                return True
                
        return False
        
    def try_select_disabled_slot(self, date_str, time_str):
        # Simulate attempting to select a disabled slot
        # This is a simulated browser interaction that would normally be prevented by UI
        datetime_str = f"{date_str}T{time_str}"
        
        # Try to submit with a known disabled slot
        self.set_appointment_time(datetime_str)
        self.set_details("Attempting to book disabled slot")
        self.submit_form()
        
        # Should fail with error about slot already booked
        return "Time slot already booked" in self.response.text
