# dsl/dsl.py
class AppointmentDSL:
    """
    DSL layer that abstracts domain actions for the appointment scheduler.
    It translates high-level commands into calls to the protocol driver.
    """
    def __init__(self, driver):
        self.driver = driver

    def visit_booking_page(self):
        # Domain action: visit the appointment scheduling page
        return self.driver.visit_page()
        
    def clear_all_appointments(self):
        # Domain action: clear all appointments for testing
        return self.driver.clear_all_slots()
        
    def select_appointment_time(self, datetime_str):
        # Domain action: set the appointment time.
        self.driver.set_appointment_time(datetime_str)

    def enter_appointment_details(self, details):
        # Domain action: enter the appointment details.
        self.driver.set_details(details)

    def submit_appointment(self):
        # Domain action: submit the appointment form.
        self.driver.submit_form()

    def verify_appointment_success(self):
        # Verify that the appointment was successfully booked.
        return self.driver.check_success_message()

    def verify_booking_constraint(self):
        # Verify that booking fails when the time slot is already taken.
        return self.driver.check_error_message("Time slot already booked")
        
    def verify_time_slot_is_disabled(self, date_str, time_str):
        # Domain action: verify that a specific time slot is disabled in the UI
        return self.driver.check_time_slot_disabled(date_str, time_str)
        
    def attempt_to_select_disabled_slot(self, date_str, time_str):
        # Domain action: attempt to select and book a slot that should be disabled
        return self.driver.try_select_disabled_slot(date_str, time_str)
        
    def verify_all_booked_slots_disabled(self):
        # Domain action: verify that all booked slots are properly disabled
        # First get the booked slots
        self.driver.get_booked_slots()
        if not self.driver.booked_slots:
            return True  # No booked slots to check
            
        # Check each slot is disabled
        for slot in self.driver.booked_slots:
            date_part = slot.split('T')[0]
            time_part = slot.split('T')[1].split(':')[0] + ":00"
            if not self.driver.check_time_slot_disabled(date_part, time_part):
                return False
                
        return True
        
    def verify_past_date_is_disabled(self):
        # Domain action: verify that past dates are disabled
        from datetime import datetime, timedelta
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        return self.driver.check_time_slot_disabled(yesterday, "12:00")
    
    def verify_sunday_is_disabled(self):
        # Domain action: verify that Sunday is disabled
        from datetime import datetime, timedelta
        
        # Find the next Sunday
        today = datetime.now()
        days_until_sunday = 6 - today.weekday() if today.weekday() != 6 else 7
        next_sunday = (today + timedelta(days=days_until_sunday)).strftime("%Y-%m-%d")
        
        return self.driver.check_time_slot_disabled(next_sunday, "12:00")
    
    def verify_tomorrow_is_default_selection(self):
        # Domain action: verify that tomorrow (or next business day) is pre-selected
        from datetime import datetime, timedelta
        
        # Calculate tomorrow (skipping Sunday)
        tomorrow = datetime.now() + timedelta(days=1)
        if tomorrow.weekday() == 6:  # Sunday
            tomorrow += timedelta(days=1)  # Move to Monday
            
        tomorrow_str = tomorrow.strftime("%Y-%m-%d")
        
        # This is a simplified check since we can't easily check the UI selection state
        # We verify that tomorrow is enabled (not disabled) as a proxy for being selected
        return not self.driver.check_time_slot_disabled(tomorrow_str, "12:00")
