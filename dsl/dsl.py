# dsl/dsl.py
class AppointmentDSL:
    """
    DSL layer that abstracts domain actions for the appointment scheduler.
    It translates high-level commands into calls to the protocol driver.
    """
    def __init__(self, driver):
        self.driver = driver

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
