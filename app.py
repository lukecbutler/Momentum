from flask import Flask, render_template, request, redirect, url_for, make_response # import portions of flask needed for app
import sqlite3 # import sqlite, needed for creating, writing to, and pulling from the database
from werkzeug.security import generate_password_hash, check_password_hash # hashes passwords & checks the hash against the security key
from datetime import date # handles dates for task deadlines

app = Flask(__name__) # create the actual application
app.secret_key = 'password'  # used in hashing passwords - replace with secure 32b random string in production
DATABASE = "tasks.db" # name of database

# used throughout the application for a quick connection to the database - returns a connection to the db
def get_db_connection():
    conn = sqlite3.connect(DATABASE) # set conn as the connection to the database
    conn.row_factory = sqlite3.Row # return the datbase as a dictionary like object
    return conn

def init_db(): # creates the tables in the database if they accidently clear - consider removing
    with get_db_connection() as conn:
        cursor = conn.cursor() # cursor acts as an sql query writer
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                date TEXT NOT NULL,
                user_id INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        conn.commit() # commit all changes made to the database

init_db() # run init_db when the application is ran, to handle database tables not being present

# Helper functions to get user info from cookies
def get_current_user_id():
    return request.cookies.get('user_id')

def get_current_username():
    return request.cookies.get('username')

# as login is our home route, send users to login when they visit the base route of our site
@app.route("/", methods=['GET', 'POST'])
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST': # occurs when users attempt to login

        # take the username & password fields & set them to variables
        username = request.form.get("username")
        password = request.form.get("password")

        # use the database connection and set as connection(conn) variable
        with get_db_connection() as conn:
            # set user variable as username from the database
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

            # if the user was found in the database, and the password enters matches that users password, continue
            if user and check_password_hash(user['password'], password):
                # create response with redirect
                resp = make_response(redirect(url_for('home')))
                # set cookies for user_id and username that expire in 30 days
                resp.set_cookie('user_id', str(user['id']), max_age=60*60*24*30)
                resp.set_cookie('username', user['username'], max_age=60*60*24*30)
                return resp
            return "Invalid username or password."
    return render_template('login.html') # the get request (just visiting the / or /login route of the page)

# shows registration page & handles new users registering
@app.route("/register", methods=["GET", "POST"])
def register():

    # take in user name & password for registration
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # hash password super duper securely
        hashed_password = generate_password_hash(password)

        try:
            # insert into the database the username & the hashed password
            with get_db_connection() as conn:
                # sql query to do said insertion
                conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
                conn.commit()
            # redirect to login so they can login via their username & password
            return redirect(url_for('login'))
        
        # if there already is a username sql throws an error
        # handle the error by returning "Username already exists"
        except sqlite3.IntegrityError:
            return "Username already exists!"
    return render_template('register.html') # get request for register (just shows the register page when they visit that )

# the mainpage of momentum - this is the display task functionality
@app.route("/home", methods=["GET", "POST"])
def home():
    # check for user_id cookie instead of session
    user_id = get_current_user_id()
    if not user_id:
        return redirect(url_for('login'))

    # if the user enters a task to display
    if request.method == "POST":

        # set the task from the task form in the index.html
        task = request.form.get('task')

        # get the date from the date form
        task_date = request.form.get('date') or date.today().isoformat()

        # if the task is not empty add the task to the users tasks, via the add task method
        if task and task.strip():
            add_task(task, user_id, task_date)

        # once the task has been added to the database, redirect them back to the home page to revent
        # the refresh re-add task error
        return redirect(url_for('home'))

    # get all tasks from the user's task list, and set them to a tasks variable
    with get_db_connection() as conn:
        tasks = conn.execute('SELECT id, task, date FROM tasks WHERE user_id = ?', 
                             (user_id,)).fetchall()

    # reformat the date to display properly on the homepage
    # format date to MM/DD/YYYY
    formatted_tasks = []

    for task in tasks:
        # convert the date to a new format
        date_parts = task['date'].split('-')  # ['YYYY', 'MM', 'DD']
        formatted_date = f"{date_parts[1]}/{date_parts[2]}/{date_parts[0]}"  # MM/DD/YYYY

        # create a new dictionary with the formatted date
        new_task = {
            'id': task['id'],
            'task': task['task'],
            'date': formatted_date
        }
        # add the task to the formatted tasks list
        formatted_tasks.append(new_task)

    # returns the index.html homepage with all tasks
    return render_template("index.html", tasks=formatted_tasks, username=get_current_username(),
                           current_date=date.today().isoformat())

# add task's user has entered
def add_task(task, user_id, task_date):
    try:
        # get database connection and pass in that specific task to the task table with the user_id and the date selected for the task
        with get_db_connection() as conn:
            conn.execute('INSERT INTO tasks (task, date, user_id) VALUES (?, ?, ?)', 
                         (task, task_date, user_id))
            conn.commit()
        return True
    # error handling for sqlite
    except sqlite3.Error:
        return False

# delete task based on task_id - makes sure a user cannot delete another users task
@app.route("/delete_task/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    # check for user_id cookie instead of session
    user_id = get_current_user_id()
    if not user_id:
        return redirect(url_for('login'))
    
    # get a database connection & deletes task based on task_id and the user_id
    with get_db_connection() as conn:
        conn.execute('DELETE FROM tasks WHERE id = ? AND user_id = ?', (task_id, user_id))
        conn.commit()
    # one task is deleted they are stay in the home route
    return redirect(url_for('home'))

# clears all tasks the user has in the task list (procrastinate)
@app.route("/clear", methods=["POST"])
def clear_database():
    # check for user_id cookie instead of session
    user_id = get_current_user_id()
    if not user_id:
        return redirect(url_for('login'))
    
    # deletes all tasks of a certain user_id
    with get_db_connection() as conn:
        conn.execute('DELETE FROM tasks WHERE user_id = ?', (user_id,))
        conn.commit()
    # they stay at the homepage once all tasks are deleted
    return redirect(url_for('home'))

# clears cookies for the user, logging them out of momentum
@app.route("/logout")
def logout():
    resp = make_response(redirect(url_for('login')))
    # Delete the authentication cookies
    resp.delete_cookie('user_id')
    resp.delete_cookie('username')
    return resp

# runs the app.py file via port 80
if __name__ == '__main__':
    app.run(debug=True, port=80, host='0.0.0.0')