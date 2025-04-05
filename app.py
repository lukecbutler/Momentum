from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from login import *

app = Flask(__name__)

# Dummy user database (in-memory dictionary)
users = {}

# Database connection
DATABASE = "tasks.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# where user adds & see's their tasks
@app.route("/", methods = ['GET', 'POST'])
@app.route("/home", methods=["GET", "POST"])
def home():
    conn = get_db_connection()
    cursor = conn.cursor()

    # This happens when the user hits the 'add task' button
    if request.method == "POST":
        add_task(request.form['task'])

    # pull all tasks from database
    tasks = cursor.execute('SELECT task FROM tasks').fetchall()
    conn.close()

    # render index.html with all tasks
    return render_template("index.html", tasks=tasks)

# function that takes a task and adds it to database
def add_task(task):
    """
    Add task to the database
    :param task: Task to be added to the database containing a string 
    """
    if not task or task == "":
        # flash("Task cannot be empty.")  #TODO: FIND WHERE TO USE THIS
        return False

    try:
        with get_db_connection() as conn:
            # You create a cursor to execute the sql commands
            cursor = conn.cursor()
            # insert task into database
            cursor.execute('''
                INSERT INTO tasks (task)
                VALUES (?)
            ''', (task,))
            conn.commit()
        return True

    except sqlite3.Error:
        # flash("Error adding task. Please try again.")  #TODO: FIND WHERE TO USE THIS
        return False


@app.route("/")

@app.route("/clear", methods=["POST"])
def clear_database():
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tasks')
        conn.commit()
    return redirect(url_for('home'))  # Redirect back to the home page

if __name__ == '__main__':
    app.run(debug=True, port=80, host='0.0.0.0')