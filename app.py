from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Database connection
DATABASE = "tasks.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/", methods=["GET", "POST"])
def home():
    conn = get_db_connection()
    cursor = conn.cursor()

    # This happens when the user hits the 'add task' button
    if request.method == "POST":
        task = request.form['task']
        # insert task into database
        cursor.execute('''
            INSERT INTO tasks (task)
            VALUES (?)
        ''', (task,))
        conn.commit()
    
    # pull all tasks from database
    tasks = cursor.execute('SELECT task FROM tasks').fetchall()
    conn.close()

    # render index.html with all tasks
    return render_template("index.html", tasks=tasks)

@app.route("/clear", methods=["POST"])
def clear_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks')  # Clear all tasks
    conn.commit()
    conn.close()
    return redirect(url_for('home'))  # Redirect back to the home page

if __name__ == '__main__':
    app.run(debug=True, port=80, host='0.0.0.0')