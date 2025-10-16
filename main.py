from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import DataRequired, Length, Email

app = Flask(__name__)
app.secret_key = "secret123"

board = [" "] * 9
player = "X"


conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS register (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")
conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS login (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")
conn.commit()


class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Register')

def check_win(p):
    b = board
    return ((b[0]==b[1]==b[2]==p) or
            (b[3]==b[4]==b[5]==p) or
            (b[6]==b[7]==b[8]==p) or
            (b[0]==b[3]==b[6]==p) or
            (b[1]==b[4]==b[7]==p) or
            (b[2]==b[5]==b[8]==p) or
            (b[0]==b[4]==b[8]==p) or
            (b[2]==b[4]==b[6]==p))

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    message = ""
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        with sqlite3.connect('users.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM register WHERE email = ?", (email,))
            existing_user = cursor.fetchone()
            if existing_user:
                message = "⚠️ Email already exists. Please go to Login."
            else:
                cursor.execute(
                    "INSERT INTO register (name, email, password) VALUES (?, ?, ?)",
                    (name, email, password)
                )
                conn.commit() 
                message = "🎉 Registered successfully! You can now log in."
                return redirect(url_for("start"))
    return render_template("register.html", form=form, message=message)

@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM register WHERE email = ? AND password = ?",
                (username, password)
            )
            existing_user = cursor.fetchone()
            if existing_user:
                cursor.execute(
                    "INSERT INTO login (email, password) VALUES (?, ?)",
                    (username, password)
                )
                conn.commit() 
                session["username"] = username
                return redirect(url_for("start"))
            else:
                message = "You are not registered. Please register first."
    return render_template("login.html", message=message)


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("home"))

@app.route("/start")
def start():
    global player
    move = request.args.get("move")
    message = ""
    if move is not None:
        move = int(move)
        if board[move] == " ":
            board[move] = player
            if check_win(player):
                message = f"Player {player} wins!"
            elif " " not in board:
                message = "It's a draw!"
            else:
                player = "O" if player == "X" else "X"
        else:
            message = "Spot taken! Try again."
    return render_template("start.html", board=board, player=player, message=message)

@app.route("/reset")
def reset():
    global board, player
    board = [" "] * 9
    player = "X"
    return redirect(url_for('start'))

if __name__ == "__main__":
    app.run(debug=True)

