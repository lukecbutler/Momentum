from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)

# Dummy user database (in-memory dictionary)
users = {}

# Database connection
DATABASE = "tasks.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Login route - now the default route
@app.route("/", methods=['GET', 'POST'])
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        if username in users and users[username] == password:
            # Redirect to home with username as parameter
            return redirect(url_for('home', username=username))
        return "Invalid username or password."
    return render_template('login.html')

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in users:
            return "Username already exists! Please choose a different one."
        else:
            users[username] = password
            return redirect(url_for('login'))
    return render_template('register.html')

# Home route - protected by URL parameter
@app.route("/home", methods=["GET", "POST"])
def home():
    username = request.args.get('username')
    if not username or username not in users:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        add_task(request.form['task'])

    tasks = cursor.execute('SELECT task FROM tasks').fetchall()
    conn.close()

    return render_template("index.html", tasks=tasks, username=username)

def add_task(task):
    if not task or task == "":
        return False

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO tasks (task)
                VALUES (?)
            ''', (task,))
            conn.commit()
        return True
    except sqlite3.Error:
        return False

@app.route("/clear", methods=["POST"])
def clear_database():
    username = request.args.get('username')
    if not username or username not in users:
        return redirect(url_for('login'))
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tasks')
        conn.commit()
    return redirect(url_for('home', username=username))

if __name__ == '__main__':
    app.run(debug=True, port=80, host='0.0.0.0')