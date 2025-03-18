# tests/test_acceptance.py
import unittest
from dsl.dsl import AppointmentDSL
from driver.driver import WebAppDriver
import time
from datetime import datetime, timedelta

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
        
    def test_display_only_available_time_slots(self):
        """
        Test that only available one-hour slots are enabled in the UI.
        """
        # Visit the booking page
        self.dsl.visit_booking_page()
        # Allow a moment for the page to load
        time.sleep(1)
        # Verify that all booked slots are properly disabled
        self.assertTrue(self.dsl.verify_all_booked_slots_disabled())

    def test_grey_out_already_booked_time_slot(self):
        """
        Test that an already booked time slot is greyed out in the date-time picker.
        """
        # First, book an appointment
        appointment_time = "2025-03-17T16:00"
        details = "Dentist appointment"
        self.dsl.select_appointment_time(appointment_time)
        self.dsl.enter_appointment_details(details)
        self.dsl.submit_appointment()
        time.sleep(1)
        
        # Visit the page again
        self.dsl.visit_booking_page()
        time.sleep(1)
        
        # Verify the time slot is greyed out
        date_part = "2025-03-17"
        time_part = "16:00"
        self.assertTrue(self.dsl.verify_time_slot_is_disabled(date_part, time_part))

    def test_successfully_book_available_time_slot(self):
        """
        Test that booking an available time slot works and then that slot becomes disabled.
        """
        # Generate a future date/time that should be available
        tomorrow = datetime.now() + timedelta(days=1)
        tomorrow = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
        date_str = tomorrow.strftime("%Y-%m-%d")
        time_str = "10:00"
        appointment_time = f"{date_str}T{time_str}"
        
        # Book the appointment
        self.dsl.select_appointment_time(appointment_time)
        self.dsl.enter_appointment_details("Team Meeting")
        self.dsl.submit_appointment()
        time.sleep(1)
        self.assertTrue(self.dsl.verify_appointment_success())
        
        # Visit the page again and verify the slot is now disabled
        self.dsl.visit_booking_page()
        time.sleep(1)
        self.assertTrue(self.dsl.verify_time_slot_is_disabled(date_str, time_str))

    def test_attempting_to_select_greyed_out_slot(self):
        """
        Test that attempting to select a greyed-out slot is prevented.
        """
        # First, book an appointment
        appointment_time = "2025-03-18T09:00"
        details = "Dentist appointment"
        self.dsl.select_appointment_time(appointment_time)
        self.dsl.enter_appointment_details(details)
        self.dsl.submit_appointment()
        time.sleep(1)
        
        # Attempt to book the same slot again (simulating a user bypassing client-side validation)
        self.assertTrue(self.dsl.attempt_to_select_disabled_slot("2025-03-18", "09:00"))
        
    def test_today_date_is_disabled(self):
        """
        Test that today's date is disabled and cannot be selected for appointments.
        """
        # Visit the booking page
        self.dsl.visit_booking_page()
        time.sleep(1)
        
        # Verify that today's date is disabled
        self.assertTrue(self.dsl.verify_today_is_disabled())
        
    def test_sunday_dates_are_disabled(self):
        """
        Test that Sundays are disabled and cannot be selected for appointments.
        """
        # Visit the booking page
        self.dsl.visit_booking_page()
        time.sleep(1)
        
        # Verify that Sunday dates are disabled
        self.assertTrue(self.dsl.verify_sunday_is_disabled())
        
    def test_tomorrow_is_default_selection(self):
        """
        Test that tomorrow (or next business day if tomorrow is Sunday) is pre-selected by default.
        """
        # Visit the booking page
        self.dsl.visit_booking_page()
        time.sleep(1)
        
        # Verify that tomorrow is the default selection
        self.assertTrue(self.dsl.verify_tomorrow_is_default_selection())
        
    def test_cannot_book_on_sunday(self):
        """
        Test that the system prevents booking appointments on Sundays.
        """
        # Find the next Sunday
        today = datetime.now()
        days_until_sunday = 6 - today.weekday() if today.weekday() != 6 else 7
        next_sunday = today + timedelta(days=days_until_sunday)
        sunday_str = next_sunday.strftime("%Y-%m-%d")
        
        # Attempt to book on Sunday (simulating a user bypassing client-side validation)
        sunday_time = f"{sunday_str}T12:00"
        self.dsl.select_appointment_time(sunday_time)
        self.dsl.enter_appointment_details("Sunday appointment")
        self.dsl.submit_appointment()
        
        # This should fail with an appropriate error message
        # Since we don't have a specific error for Sundays, we'll just check that it's not successful
        time.sleep(1)
        self.assertFalse(self.dsl.verify_appointment_success())
        
    def test_cannot_book_today(self):
        """
        Test that the system prevents booking appointments for today.
        """
        # Get today's date
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        # Attempt to book today (simulating a user bypassing client-side validation)
        today_time = f"{today_str}T15:00"
        self.dsl.select_appointment_time(today_time)
        self.dsl.enter_appointment_details("Same-day appointment")
        self.dsl.submit_appointment()
        
        # This should fail
        time.sleep(1)
        self.assertFalse(self.dsl.verify_appointment_success())

if __name__ == '__main__':
    unittest.main()
