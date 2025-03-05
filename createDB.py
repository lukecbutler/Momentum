import sqlite3

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect("tasks.db")
cursor = conn.cursor()

# Create the Workouts table
cursor.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task TEXT NOT NULL
);
''')