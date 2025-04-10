import sqlite3

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect("tasks.db")
cursor = conn.cursor()

# Create the tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task TEXT NOT NULL
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS userstable (
    userID INTEGER PRIMARY KEY NOT NULL,
    username TEXT NOT NULL,
    password TEXT NOT NULL
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS tasktable (
    taskID INTEGER PRIMARY KEY NOT NULL,
    userID INT NOT NULL,
    Description TEXT NOT NULL,
    Date TEXT NOT NULL,
    FOREIGN KEY (userID) REFERENCES userstable(userID)
);
''')

conn.close()