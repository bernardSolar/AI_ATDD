In this project, I applied Dave Farley’s ATDD approach using his Four-Layer Model. Here’s how each layer was used in the creation of the appointment scheduler:

1. **Acceptance Test Layer:**  
   - **What It Is:** These tests serve as the executable specifications of your application, describing in plain, domain-specific language what the system should do.  
   - **How We Used It:**  
     - In `tests/test_acceptance.py`, we wrote tests that simulate a user booking an appointment and verify that the key business rule (no overlapping appointments within the same one-hour slot) is enforced.  
     - The tests are high-level, focusing on the “what” rather than the “how.”

2. **Domain-Specific Language (DSL) Layer:**  
   - **What It Is:** The DSL abstracts domain actions into clear, readable commands. It converts these high-level commands into calls that the underlying system can execute.  
   - **How We Used It:**  
     - In `dsl/dsl.py`, we created an `AppointmentDSL` class with methods like `select_appointment_time`, `enter_appointment_details`, and `submit_appointment`.  
     - This layer allows our acceptance tests to be written in a domain-friendly way, hiding the implementation details of how these actions are actually performed.

3. **Protocol Driver Layer:**  
   - **What It Is:** This layer deals with the low-level details of interacting with the system (for instance, simulating browser actions or handling HTTP requests).  
   - **How We Used It:**  
     - In `driver/driver.py`, we implemented a `WebAppDriver` class that simulates user interactions (like setting form values and submitting the form) by making HTTP requests to our Flask app.  
     - It abstracts the technicalities of the underlying transport mechanism, so the DSL remains focused solely on domain logic.

4. **System Under Test (SUT):**  
   - **What It Is:** The actual web application that implements the business logic.  
   - **How We Used It:**  
     - In `app/app.py`, we built a simple Flask web app that handles appointment scheduling, including the enforcement of the one-hour booking rule.  
     - The SUT is completely decoupled from the test code—it’s accessed indirectly through the DSL and protocol driver layers.

### Summary

By following Dave Farley’s ATDD approach, we:

- **Raised the level of abstraction:** Our acceptance tests (the specifications) drive the development, ensuring we focus on what the application must achieve rather than the nitty-gritty of how it does so.
- **Separated concerns:** Each layer has a distinct responsibility—from high-level domain behavior (acceptance tests and DSL) to low-level implementation details (protocol driver) and the core business logic (SUT).
- **Facilitated maintenance and clarity:** If the underlying implementation needs to change (for example, switching from Selenium-based interactions to direct HTTP calls), we only need to update the protocol driver while keeping the acceptance tests and DSL intact.

This layered approach not only aligns with Dave Farley’s vision for using acceptance tests as the specification but also ensures that your development process remains clear, maintainable, and closely tied to the actual business requirements.