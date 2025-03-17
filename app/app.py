# app/app.py
from flask import Flask, request, render_template_string, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
DATABASE = 'appointments.db'

def init_db():
    # Initialize the SQLite database with an appointments table.
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS appointments
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  appointment_time TEXT,
                  details TEXT)''')
    conn.commit()
    conn.close()

def setup():
    # Manually initialize the database.
    init_db()

@app.route('/', methods=['GET', 'POST'])
def schedule():
    if request.method == 'POST':
        appointment_time = request.form.get('appointment_time')
        details = request.form.get('details')
        try:
            # Convert appointment_time to a datetime object (expects ISO format)
            appt_dt = datetime.fromisoformat(appointment_time)
        except Exception:
            return "Invalid datetime format", 400

        # Check the booking constraint: no overlapping appointments in the same one-hour slot.
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("SELECT appointment_time FROM appointments")
        existing = c.fetchall()
        for (existing_time_str,) in existing:
            existing_time = datetime.fromisoformat(existing_time_str)
            if (appt_dt.year == existing_time.year and
                appt_dt.month == existing_time.month and
                appt_dt.day == existing_time.day and
                appt_dt.hour == existing_time.hour):
                conn.close()
                return "Time slot already booked", 400

        # Insert the appointment into the database.
        c.execute("INSERT INTO appointments (appointment_time, details) VALUES (?, ?)",
                  (appointment_time, details))
        conn.commit()
        conn.close()
        return redirect(url_for('schedule'))

    html = '''
    <!doctype html>
    <html>
    <head>
        <title>Appointment Scheduler</title>
    </head>
    <body>
        <h1>Book an Appointment</h1>
        <form method="post">
            <label for="appointment_time">Appointment Time (ISO format, e.g., 2025-03-17T14:00):</label>
            <input type="datetime-local" id="appointment_time" name="appointment_time" required><br><br>
            <label for="details">Details:</label><br>
            <textarea id="details" name="details" rows="4" cols="50" required></textarea><br><br>
            <input type="submit" value="Book Appointment">
        </form>
    </body>
    </html>
    '''
    return render_template_string(html)

if __name__ == '__main__':
    setup()  # Manually initialize the database before starting the server
    app.run(port=8999, debug=True)
