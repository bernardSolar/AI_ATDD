# AI_ATDD
This app was auto generated using this prompt:

---

**Prompt:**

> **Task:**  
> Develop a simple browser-based appointment scheduler web app with the following requirements:  
> - The user interface should include a "date-time picker" component for selecting the appointment time and a text area for entering the appointment details.  
> - When the user finishes entering their appointment, the details should be stored.  
> - The app must enforce that no two appointments can be booked in the same one-hour time slot.  
> - The app will run locally on a Mac at `http://localhost:8999`.  
> - Use a simple SQLite database as the backend for storing appointments.
> 
> **Approach:**  
> Follow an Acceptance Test-Driven Development (ATDD) methodology using a Four-Layer Model:
> 
> 1. **Acceptance Test Layer:**  
>    - Write high-level, executable acceptance tests that clearly define the desired behaviors in domain language.  
>    - These tests can be written in a cucumber/gherkin style or any high-level format that best expresses the specifications.
> 
> 2. **Domain-Specific Language (DSL) Layer:**  
>    - Create a DSL that abstracts the domain actions (e.g., "select appointment time", "enter appointment details", "submit appointment", "verify booking constraint").  
>    - The DSL should convert these high-level commands into actions that interact with the underlying system.
> 
> 3. **Protocol Driver Layer:**  
>    - Implement a driver that handles low-level details like simulating browser interactions (for the date-time picker and text area) and communicating with the SQLite backend.
> 
> 4. **System Under Test (SUT):**  
>    - The actual web application (the appointment scheduler) that runs on `http://localhost:8999`.  
>    - The SUT should only be interacted with indirectly via the DSL and protocol driver layers.
> 
> **Objective:**  
> Generate a sample project structure that includes:
> - A set of acceptance tests that serve as executable specifications for the appointment scheduler.
> - A DSL layer that translates domain-specific commands into protocol driver calls.
> - A protocol driver that simulates the browser-based interactions and manages data storage in SQLite.
> - Integration of these components in a way that the acceptance tests enforce the key constraint (no appointment overlapping within the same one-hour slot).
> 
> Include inline comments to explain the purpose of each component and layer. Let's get started!

---

This prompt instructs the LLM to build an ATDD-based solution where acceptance tests guide the creation of the DSL, the protocol driver, and ultimately the SUT implementation, all while ensuring your specific business rules are met.