import sqlite3
import datetime

# Connect to the database (create it if it doesn't exist)
conn = sqlite3.connect('db.sqlite3')

# Create a table for the temperature readings
conn.execute('''CREATE TABLE IF NOT EXISTS temperature_readings
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
             temperature REAL,
             arduino_id INTEGER,
             created_at DATETIME)''')

# Save the changes and close the connection
conn.commit()
