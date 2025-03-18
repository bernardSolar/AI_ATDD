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
        # Use a future date (day after tomorrow to avoid conflicts with other tests)
        future_date = datetime.now() + timedelta(days=2)
        if future_date.weekday() == 6:  # Skip Sunday
            future_date += timedelta(days=1)
        future_date = future_date.replace(hour=14, minute=0, second=0, microsecond=0)
        appointment_time = future_date.strftime("%Y-%m-%dT%H:%M")
        
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
        # Use a future date (3 days ahead to avoid conflicts)
        future_date = datetime.now() + timedelta(days=3)
        if future_date.weekday() == 6:  # Skip Sunday
            future_date += timedelta(days=1)
        future_date = future_date.replace(hour=15, minute=0, second=0, microsecond=0)
        appointment_time = future_date.strftime("%Y-%m-%dT%H:%M")
        
        # First, book an appointment.
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
        # Use a future date (4 days ahead to avoid conflicts)
        future_date = datetime.now() + timedelta(days=4)
        if future_date.weekday() == 6:  # Skip Sunday
            future_date += timedelta(days=1)
        future_date = future_date.replace(hour=16, minute=0, second=0, microsecond=0)
        appointment_time = future_date.strftime("%Y-%m-%dT%H:%M")
        date_part = future_date.strftime("%Y-%m-%d")
        time_part = "16:00"
        
        # First, book an appointment
        details = "Dentist appointment"
        self.dsl.select_appointment_time(appointment_time)
        self.dsl.enter_appointment_details(details)
        self.dsl.submit_appointment()
        time.sleep(1)
        
        # Visit the page again
        self.dsl.visit_booking_page()
        time.sleep(1)
        
        # Verify the time slot is greyed out
        self.assertTrue(self.dsl.verify_time_slot_is_disabled(date_part, time_part))

    def test_successfully_book_available_time_slot(self):
        """
        Test that booking an available time slot works and then that slot becomes disabled.
        """
        # Use day after tomorrow to avoid potential conflicts
        # (some systems might be using tomorrow already in another test)
        future_date = datetime.now() + timedelta(days=6)  # Use 6 days ahead to avoid conflicts
        if future_date.weekday() == 6:  # Skip Sunday
            future_date += timedelta(days=1)
        future_date = future_date.replace(hour=10, minute=0, second=0, microsecond=0)
        date_str = future_date.strftime("%Y-%m-%d")
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
        # Use a future date (5 days ahead to avoid conflicts)
        future_date = datetime.now() + timedelta(days=5)
        if future_date.weekday() == 6:  # Skip Sunday
            future_date += timedelta(days=1)
        future_date = future_date.replace(hour=9, minute=0, second=0, microsecond=0)
        appointment_time = future_date.strftime("%Y-%m-%dT%H:%M")
        date_part = future_date.strftime("%Y-%m-%d")
        time_part = "09:00"
        
        # First, book an appointment
        details = "Dentist appointment"
        self.dsl.select_appointment_time(appointment_time)
        self.dsl.enter_appointment_details(details)
        self.dsl.submit_appointment()
        time.sleep(1)
        
        # Attempt to book the same slot again (simulating a user bypassing client-side validation)
        self.assertTrue(self.dsl.attempt_to_select_disabled_slot(date_part, time_part))
        
    def test_past_date_is_disabled(self):
        """
        Test that past dates are disabled and cannot be selected for appointments.
        """
        # Visit the booking page
        self.dsl.visit_booking_page()
        time.sleep(1)
        
        # Create a date in the past
        past_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Verify that past date is disabled
        self.assertTrue(self.driver.check_time_slot_disabled(past_date, "12:00"))
        
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
        
    def test_cannot_book_past_date(self):
        """
        Test that the system prevents booking appointments for past dates.
        """
        # Get a past date
        past_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Attempt to book past date (simulating a user bypassing client-side validation)
        past_time = f"{past_date}T15:00"
        self.dsl.select_appointment_time(past_time)
        self.dsl.enter_appointment_details("Past appointment")
        self.dsl.submit_appointment()
        
        # This should fail
        time.sleep(1)
        self.assertFalse(self.dsl.verify_appointment_success())

if __name__ == '__main__':
    unittest.main()
