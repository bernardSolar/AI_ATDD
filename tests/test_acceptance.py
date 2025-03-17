# tests/test_acceptance.py
import unittest
from dsl.dsl import AppointmentDSL
from driver.driver import WebAppDriver
import time

class TestAppointmentScheduler(unittest.TestCase):
    """
    Acceptance tests for the Appointment Scheduler app.
    """

    @classmethod
    def setUpClass(cls):
        # Optionally, code to ensure the SUT is running could be placed here.
        # For this example, we assume that the app is already running on localhost:8999.
        pass

    def setUp(self):
        # Initialize the protocol driver and DSL layer.
        self.driver = WebAppDriver("http://localhost:8999")
        self.dsl = AppointmentDSL(self.driver)

    def test_successful_appointment_booking(self):
        """
        Test that an appointment is successfully booked.
        """
        appointment_time = "2025-03-17T14:00"
        details = "Doctor appointment"
        self.dsl.select_appointment_time(appointment_time)
        self.dsl.enter_appointment_details(details)
        self.dsl.submit_appointment()
        # Allow a moment for the app to process the booking.
        time.sleep(1)
        self.assertTrue(self.dsl.verify_appointment_success())

    def test_overlapping_appointment_not_allowed(self):
        """
        Test that the system prevents booking two appointments in the same one-hour slot.
        """
        # First, book an appointment.
        appointment_time = "2025-03-17T15:00"
        details = "Meeting with client"
        self.dsl.select_appointment_time(appointment_time)
        self.dsl.enter_appointment_details(details)
        self.dsl.submit_appointment()
        time.sleep(1)
        self.assertTrue(self.dsl.verify_appointment_success())

        # Attempt to book another appointment in the same time slot.
        self.dsl.select_appointment_time(appointment_time)  # Same one-hour slot.
        self.dsl.enter_appointment_details("Another appointment")
        self.dsl.submit_appointment()
        time.sleep(1)
        self.assertTrue(self.dsl.verify_booking_constraint())

if __name__ == '__main__':
    unittest.main()
