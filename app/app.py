# app/app.py
from flask import Flask, request, render_template_string, redirect, url_for, jsonify
import sqlite3
from datetime import datetime, timedelta
import json

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

def get_booked_slots():
    # Get all booked time slots from the database
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT appointment_time FROM appointments")
    booked_slots = [datetime.fromisoformat(row[0]) for row in c.fetchall()]
    conn.close()
    return booked_slots

@app.route('/api/booked-slots', methods=['GET'])
def booked_slots_api():
    # API endpoint to get booked slots
    booked_slots = get_booked_slots()
    # Format the slots as ISO strings
    formatted_slots = [slot.isoformat() for slot in booked_slots]
    return jsonify(formatted_slots)
    
@app.route('/api/clear-slots', methods=['POST'])
def clear_slots_api():
    # API endpoint to clear all booked slots (for testing)
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("DELETE FROM appointments")
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "All appointments cleared"})

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

        # Check if date is in the past
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if appt_dt.date() < today.date():
            return "Cannot book appointments for past dates", 400
            
        # Check if date is a Sunday
        if appt_dt.weekday() == 6:  # Sunday is 6 in Python's weekday()
            return "Cannot book appointments on Sundays", 400
            
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

    # Get booked slots for the UI (with cache-busting timestamp)
    cache_buster = datetime.now().timestamp()
    booked_slots = get_booked_slots()
    formatted_slots = json.dumps([slot.isoformat() for slot in booked_slots])
    
    # Generate dates for the next 7 days
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    next_7_days = [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    
    html = f'''
    <!doctype html>
    <html>
    <head>
        <title>Appointment Scheduler</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f8f9fa;
                color: #333;
            }}
            .container {{
                background-color: white;
                border-radius: 10px;
                padding: 25px;
                box-shadow: 0 3px 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #2c3e50;
                margin-bottom: 20px;
                text-align: center;
                font-size: 28px;
            }}
            h2 {{
                color: #3498db;
                margin: 20px 0 10px;
                font-size: 22px;
                border-bottom: 2px solid #f0f0f0;
                padding-bottom: 8px;
            }}
            label {{
                display: block;
                margin-top: 15px;
                margin-bottom: 8px;
                font-weight: 600;
                color: #555;
            }}
            input, textarea {{
                width: 100%;
                padding: 12px;
                margin-bottom: 20px;
                border: 1px solid #ddd;
                border-radius: 6px;
                box-sizing: border-box;
                transition: border 0.3s;
                font-size: 16px;
            }}
            input:focus, textarea:focus {{
                border-color: #3498db;
                outline: none;
            }}
            textarea {{
                min-height: 120px;
                resize: vertical;
            }}
            button {{
                background-color: #3498db;
                border: none;
                color: white;
                padding: 14px 20px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 16px;
                font-weight: 600;
                width: 100%;
                transition: background-color 0.3s;
            }}
            button:hover {{
                background-color: #2980b9;
            }}
            .date-selector {{
                display: grid;
                grid-template-columns: repeat(7, 1fr);
                grid-gap: 8px;
                margin-bottom: 20px;
                padding-bottom: 10px;
            }}
            .date-card {{
                flex: 0 0 auto;
                width: auto;
                height: auto;
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 6px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                transition: all 0.2s ease;
                padding: 8px 4px;
            }}
            .date-card:hover {{
                border-color: #3498db;
                background-color: #e3f2fd;
            }}
            .date-card.selected {{
                border-color: #3498db;
                background-color: #e3f2fd;
                font-weight: bold;
            }}
            .date-day {{
                font-size: 16px;
                font-weight: 600;
                color: #2c3e50;
            }}
            .date-weekday {{
                font-size: 12px;
                color: #7f8c8d;
                margin-top: 3px;
            }}
            .date-month {{
                font-size: 11px;
                color: #95a5a6;
                margin-top: 2px;
            }}
            .date-grid-header {{
                display: grid;
                grid-template-columns: repeat(7, 1fr);
                margin-bottom: 5px;
                text-align: center;
            }}
            .weekday-header {{
                font-size: 12px;
                font-weight: 600;
                color: #7f8c8d;
            }}
            .weekday-header:first-child {{
                color: #e74c3c; /* Red color for Sunday */
            }}
            .month-navigation {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
            }}
            .month-nav-btn {{
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                color: #3498db;
                padding: 8px 15px;
                border-radius: 4px;
                cursor: pointer;
                font-weight: bold;
                width: auto;
                transition: all 0.2s ease;
            }}
            .month-nav-btn:hover {{
                background-color: #e3f2fd;
                border-color: #3498db;
            }}
            .month-nav-btn:disabled {{
                opacity: 0.5;
                cursor: not-allowed;
                background-color: #f0f0f0;
                color: #868e96;
                border-color: #dee2e6;
            }}
            .current-month {{
                font-size: 18px;
                font-weight: 600;
                color: #2c3e50;
                text-align: center;
            }}
            .time-slots {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
                gap: 10px;
                margin-bottom: 20px;
            }}
            .time-slot {{
                padding: 12px;
                background-color: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 6px;
                text-align: center;
                cursor: pointer;
                transition: all 0.2s ease;
            }}
            .time-slot:hover {{
                border-color: #3498db;
                background-color: #e3f2fd;
            }}
            .time-slot.selected {{
                border-color: #3498db;
                background-color: #e3f2fd;
                font-weight: bold;
            }}
            .time-slot.disabled {{
                background-color: #f1f1f1;
                border-color: #e0e0e0;
                color: #bdbdbd;
                cursor: not-allowed;
                text-decoration: line-through;
                opacity: 0.7;
            }}
            .booked-slots-list {{
                margin-top: 30px;
                padding: 15px;
                background-color: #f5f5f5;
                border-radius: 8px;
                border-left: 4px solid #e74c3c;
            }}
            .hidden {{
                display: none;
            }}
            .message {{
                padding: 15px;
                margin-bottom: 20px;
                border-radius: 6px;
                text-align: center;
            }}
            .info {{
                background-color: #d1ecf1;
                color: #0c5460;
                border: 1px solid #bee5eb;
            }}
            .error {{
                background-color: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }}
            .success {{
                background-color: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }}
            @media (max-width: 600px) {{
                .time-slots {{
                    grid-template-columns: repeat(4, 1fr);
                }}
                .date-selector {{
                    grid-template-columns: repeat(4, 1fr);
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Book a Delivery Slot</h1>
            
            <form method="post" id="appointmentForm">
                <h2>1. Select a Date</h2>
                <div class="month-navigation">
                    <button type="button" id="prevMonth" class="month-nav-btn">&larr; Prev</button>
                    <div id="currentMonthDisplay" class="current-month">March 2025</div>
                    <button type="button" id="nextMonth" class="month-nav-btn">Next &rarr;</button>
                </div>
                <div class="date-grid-header">
                    <div class="weekday-header">Sun</div>
                    <div class="weekday-header">Mon</div>
                    <div class="weekday-header">Tue</div>
                    <div class="weekday-header">Wed</div>
                    <div class="weekday-header">Thu</div>
                    <div class="weekday-header">Fri</div>
                    <div class="weekday-header">Sat</div>
                </div>
                <div class="date-selector" id="dateSelector"></div>
                
                <h2>2. Select a Time</h2>
                <div class="time-slots" id="timeSlots"></div>
                
                <input type="hidden" id="appointment_time" name="appointment_time">
                
                <h2>3. Add Delivery Notes (Optional)</h2>
                <textarea id="details" name="details" placeholder="e.g. Notes for driver, feedback or product suggestions..." required></textarea>
                
                <button type="submit" id="submitBtn">Book Delivery</button>
            </form>
            
            <div id="bookingMessage" class="message info hidden"></div>
            
            <div class="booked-slots-list">
                <h2>Already Booked Time Slots</h2>
                <div id="slots-list"></div>
            </div>
        </div>

        <script>
            // Store the booked slots from the server
            const bookedSlots = {formatted_slots};
            const bookedDatesMap = new Map();
            
            // Current view state
            let currentViewMonth = new Date().getMonth();
            let currentViewYear = new Date().getFullYear();
            let selectedDateStr = null;
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            
            // Parse booked slots into a map for faster lookup
            bookedSlots.forEach(slot => {{
                const date = new Date(slot);
                const dateStr = date.toISOString().split('T')[0];
                const hour = date.getHours();
                
                if (!bookedDatesMap.has(dateStr)) {{
                    bookedDatesMap.set(dateStr, new Set());
                }}
                bookedDatesMap.get(dateStr).add(hour);
            }});
            
            // Update the month display
            function updateMonthDisplay() {{
                const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 
                                    'July', 'August', 'September', 'October', 'November', 'December'];
                
                document.getElementById('currentMonthDisplay').textContent = 
                    monthNames[currentViewMonth] + ' ' + currentViewYear;
                
                // Update prev month button state - disable if it would go to a past month
                const prevMonthDate = new Date(currentViewYear, currentViewMonth - 1, 1);
                const currentMonthStart = new Date(today.getFullYear(), today.getMonth(), 1);
                
                document.getElementById('prevMonth').disabled = prevMonthDate < currentMonthStart;
            }}
            
            // Set up date selector
            function setupDateSelector() {{
                const dateSelector = document.getElementById('dateSelector');
                dateSelector.innerHTML = ''; // Clear existing calendar
                
                // Calculate the first day of the month grid view
                const firstDayOfMonth = new Date(currentViewYear, currentViewMonth, 1);
                const startDate = new Date(firstDayOfMonth);
                startDate.setDate(1 - startDate.getDay()); // Go back to the previous Sunday
                
                // Update the month display
                updateMonthDisplay();
                
                // Generate a calendar grid (6 weeks = 42 days)
                for (let i = 0; i < 42; i++) {{
                    const date = new Date(startDate);
                    date.setDate(startDate.getDate() + i);
                    
                    const dateStr = date.toISOString().split('T')[0];
                    const dayNum = date.getDate();
                    const month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][date.getMonth()];
                    
                    // Check if this date is from the current view month
                    const isCurrentViewMonth = date.getMonth() === currentViewMonth && 
                                               date.getFullYear() === currentViewYear;
                    const isPastDate = date < today;
                    const isSunday = date.getDay() === 0; // Sunday is day 0
                    const isToday = dateStr === today.toISOString().split('T')[0];
                    
                    const dateCard = document.createElement('div');
                    dateCard.className = 'date-card';
                    
                    // Style dates appropriately
                    if (!isCurrentViewMonth) {{
                        dateCard.style.opacity = '0.5';
                        dateCard.style.backgroundColor = '#f8f8f8';
                    }}
                    
                    if (isPastDate || isSunday || isToday) {{
                        dateCard.style.opacity = '0.5';
                        dateCard.style.backgroundColor = '#f0f0f0';
                        dateCard.style.cursor = 'not-allowed';
                    }}
                    
                    // Add special styling for Sundays
                    if (isSunday) {{
                        dateCard.style.backgroundColor = '#ffe5e5';
                        dateCard.style.color = '#999';
                        dateCard.title = 'Sundays are not available for appointments';
                    }}
                    
                    // Highlight today's date with light green background
                    if (isToday) {{
                        dateCard.style.backgroundColor = '#d4edda'; // Light green
                        dateCard.style.color = '#333';
                        dateCard.style.borderColor = '#28a745'; // Darker green border
                        dateCard.style.borderWidth = '2px';
                        dateCard.style.fontWeight = 'bold';
                        dateCard.title = 'Appointments must be booked at least one day in advance';
                    }}
                    
                    dateCard.dataset.date = dateStr;
                    
                    const dayDiv = document.createElement('div');
                    dayDiv.className = 'date-day';
                    dayDiv.textContent = dayNum;
                    
                    const monthDiv = document.createElement('div');
                    monthDiv.className = 'date-month';
                    monthDiv.textContent = month;
                    
                    dateCard.appendChild(dayDiv);
                    dateCard.appendChild(monthDiv);
                    
                    // Only add click handler for future dates (not today) that are not Sundays
                    if (!isPastDate && !isSunday && !isToday) {{
                        dateCard.addEventListener('click', () => {{
                            // Deselect all dates
                            document.querySelectorAll('.date-card').forEach(card => {{
                                card.classList.remove('selected');
                            }});
                            
                            // Select this date
                            dateCard.classList.add('selected');
                            selectedDateStr = dateStr;
                            
                            // Update time slots
                            updateTimeSlots(dateStr);
                        }});
                    }}
                    
                    dateSelector.appendChild(dateCard);
                    
                    // Select the previously selected date if it's visible in this month
                    // (not if it's a Sunday or today)
                    if ((!isSunday) && (!isToday) && (selectedDateStr && dateStr === selectedDateStr)) {{
                        dateCard.classList.add('selected');
                        updateTimeSlots(dateStr);
                    }}
                }}
            }}
            
            // Set up navigation buttons
            function setupNavigation() {{
                // Previous month button
                document.getElementById('prevMonth').addEventListener('click', () => {{
                    // Don't allow navigating to past months
                    const prevMonthDate = new Date(currentViewYear, currentViewMonth - 1, 1);
                    const currentMonthStart = new Date(today.getFullYear(), today.getMonth(), 1);
                    
                    if (prevMonthDate >= currentMonthStart) {{
                        currentViewMonth--;
                        if (currentViewMonth < 0) {{
                            currentViewMonth = 11;
                            currentViewYear--;
                        }}
                        setupDateSelector();
                    }}
                }});
                
                // Next month button
                document.getElementById('nextMonth').addEventListener('click', () => {{
                    currentViewMonth++;
                    if (currentViewMonth > 11) {{
                        currentViewMonth = 0;
                        currentViewYear++;
                    }}
                    setupDateSelector();
                }});
            }}
            
            // Update time slots based on selected date
            function updateTimeSlots(dateStr) {{
                const timeSlots = document.getElementById('timeSlots');
                timeSlots.innerHTML = '';
                
                // Business hours: 8:00 AM to 8:00 PM
                for (let hour = 8; hour <= 20; hour++) {{
                    const timeSlot = document.createElement('div');
                    const isBooked = bookedDatesMap.has(dateStr) && bookedDatesMap.get(dateStr).has(hour);
                    
                    timeSlot.className = isBooked ? 'time-slot disabled' : 'time-slot';
                    timeSlot.textContent = hour + ':00';
                    timeSlot.dataset.hour = hour;
                    timeSlot.dataset.date = dateStr;
                    
                    if (!isBooked) {{
                        timeSlot.addEventListener('click', () => {{
                            // Deselect all time slots
                            document.querySelectorAll('.time-slot').forEach(slot => {{
                                slot.classList.remove('selected');
                            }});
                            
                            // Select this time slot
                            timeSlot.classList.add('selected');
                            
                            // Update hidden input with selected date and time
                            const selectedDateTime = dateStr + 'T' + (hour < 10 ? '0' + hour : hour) + ':00:00';
                            document.getElementById('appointment_time').value = selectedDateTime;
                            
                            document.getElementById('bookingMessage').textContent = 
                                'You are booking a delivery for ' + 
                                new Date(selectedDateTime).toLocaleString() + '.';
                            document.getElementById('bookingMessage').classList.remove('hidden');
                        }});
                    }}
                    
                    timeSlots.appendChild(timeSlot);
                }}
            }}
            
            // Display already booked slots
            function displayBookedSlots() {{
                const slotsList = document.getElementById('slots-list');
                
                if (bookedSlots.length === 0) {{
                    slotsList.innerHTML = '<p>No slots currently booked.</p>';
                }} else {{
                    // Group booked slots by date
                    const bookingsByDate = Object.create(null);
                    
                    bookedSlots.forEach(slot => {{
                        const date = new Date(slot);
                        const dateStr = date.toLocaleDateString();
                        
                        if (!bookingsByDate[dateStr]) {{
                            bookingsByDate[dateStr] = [];
                        }}
                        
                        bookingsByDate[dateStr].push(date.getHours() + ':00');
                    }});
                    
                    // Display bookings by date
                    const datesList = document.createElement('ul');
                    datesList.style.paddingLeft = '20px';
                    
                    Object.keys(bookingsByDate).forEach(date => {{
                        const listItem = document.createElement('li');
                        const dateText = document.createElement('strong');
                        dateText.textContent = date + ': ';
                        
                        listItem.appendChild(dateText);
                        listItem.appendChild(document.createTextNode(bookingsByDate[date].join(', ')));
                        datesList.appendChild(listItem);
                    }});
                    
                    slotsList.innerHTML = '';
                    slotsList.appendChild(datesList);
                }}
            }}
            
            // Form submission validation
            document.getElementById('appointmentForm').addEventListener('submit', function(e) {{
                const appointmentTime = document.getElementById('appointment_time').value;
                
                if (!appointmentTime) {{
                    e.preventDefault();
                    alert('Please select a date and time for your appointment.');
                }}
            }});
            
            // Initialize the appointment scheduler
            window.addEventListener('DOMContentLoaded', () => {{
                // Refresh data each time page loads to prevent caching issues
                fetch('/api/booked-slots?' + new Date().getTime())
                    .then(response => response.json())
                    .then(data => {{
                        // Update booked slots with fresh data
                        bookedSlots.length = 0;
                        data.forEach(slot => bookedSlots.push(slot));
                        
                        // Now initialize with fresh data
                        setupNavigation();  // Set up month navigation buttons
                        setupDateSelector(); // Set up initial calendar
                        displayBookedSlots(); // Display list of booked slots
                        
                        // Initialize the current month display
                        updateMonthDisplay();
                    }})
                    .catch(error => {{
                        console.error('Error fetching booked slots:', error);
                        
                        // Fall back to default initialization
                        setupNavigation();
                        setupDateSelector();
                        displayBookedSlots();
                        updateMonthDisplay();
                    }});
                
                // Select tomorrow as the default date since today is not available
                const tomorrow = new Date(today);
                tomorrow.setDate(tomorrow.getDate() + 1);
                // Skip Sunday
                if (tomorrow.getDay() === 0) {{
                    tomorrow.setDate(tomorrow.getDate() + 1);
                }}
                selectedDateStr = tomorrow.toISOString().split('T')[0];
                
                // Find and select tomorrow's date card
                setTimeout(() => {{
                    const tomorrowCard = document.querySelector('.date-card[data-date="' + selectedDateStr + '"]');
                    if (tomorrowCard && !tomorrowCard.classList.contains('selected')) {{
                        document.querySelectorAll('.date-card').forEach(card => {{
                            card.classList.remove('selected');
                        }});
                        tomorrowCard.classList.add('selected');
                        updateTimeSlots(selectedDateStr);
                    }}
                }}, 100);
            }});
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

if __name__ == '__main__':
    setup()  # Manually initialize the database before starting the server
    app.run(port=8999, debug=True)