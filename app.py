from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'password'  # Replace with a real secret key in production

# Database connection
DATABASE = "tasks.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn
 
# Initialize database with users table
def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Create users table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        # Create tasks table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                user_id INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        conn.commit()

init_db()

@app.route("/", methods=['GET', 'POST'])
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        with get_db_connection() as conn:
            cursor = conn.cursor()
            user = cursor.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                return redirect(url_for('home'))
            return "Invalid username or password."
    return render_template('login.html')

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        hashed_password = generate_password_hash(password)

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', 
                               (username, hashed_password))
                conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "Username already exists! Please choose a different one."
    return render_template('register.html')

@app.route("/home", methods=["GET", "POST"])
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == "POST":
        task = request.form.get('task')
        if task and task.strip():
            add_task(task, session['user_id'])

    with get_db_connection() as conn:
        cursor = conn.cursor()
        tasks = cursor.execute('SELECT id, task FROM tasks WHERE user_id = ?', (session['user_id'],)).fetchall()

    return render_template("index.html", tasks=tasks, username=session['username'])

def add_task(task, user_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO tasks (task, user_id) VALUES (?, ?)', (task, user_id))
            conn.commit()
        return True
    except sqlite3.Error:
        return False

@app.route("/delete_task/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Verify the task belongs to the current user before deleting
        cursor.execute('DELETE FROM tasks WHERE id = ? AND user_id = ?', 
                      (task_id, session['user_id']))
        conn.commit()
    return redirect(url_for('home'))

@app.route("/clear", methods=["POST"])
def clear_database():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tasks WHERE user_id = ?', (session['user_id'],))
        conn.commit()
    return redirect(url_for('home'))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=80, host='0.0.0.0')