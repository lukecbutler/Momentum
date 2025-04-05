from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Dummy user database (in-memory dictionary)
users = {}

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in users:
            return "Username already exists! Please choose a different one."
        else:
            # creates a new key-value pair in the users dictionary
            users[username] = password # username is the key ; password is the value
            # redirects user to login page after successful registration
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        # checks if the username is a key in the user dict, 
        # and if the password is associated with that particular username
        if username in users and users[username] == password:
            return f"Welcome, {username}! You are now logged in."
        return "Invalid username or password."
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True, port=80, host='0.0.0.0')