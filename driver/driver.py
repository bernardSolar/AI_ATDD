# driver/driver.py
import requests

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
        # Success is indicated by a redirect or a 200 OK.
        return self.response.status_code in (200, 302)

    def check_error_message(self, expected_message):
        # Check if the expected error message is present in the response.
        return expected_message in self.response.text
