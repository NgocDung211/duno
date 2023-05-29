import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helper import login_required
from flask_mail import Mail, Message
import random


# Congifure application
app = Flask(__name__)

app.secret_key = 'NgocDung211'

app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"

app.config['MAIL_SERVER'] = 'smtp-relay.sendinblue.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'dungdodz@gmail.com'
app.config['MAIL_PASSWORD'] = 'x3p8TOAsUZhLrqbv'

mail = Mail(app)

db = SQL("sqlite:///project.db")

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "GET":
        return render_template("index.html")
    else:
        current_id = session["user_id"]
        quote = request.form.get("quote")
        if not quote:
            flash("Please enter a quote")
            return redirect("/")
        db.execute("INSERT INTO quotes (user_id, quote) VALUES(?, ?)",current_id,quote)
        return redirect("/")
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        session.clear()
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            flash("Please enter your username and password")
            return redirect("/login")  # Redirect to the login page

        try:
            user_infor = db.execute("SELECT * FROM users WHERE name = ?", username)
        except:
            flash("Get problem please try again")
            return redirect("/login")
        hash_password = user_infor[0]["password"]
        if check_password_hash(hash_password,password) == False:
            flash("Password is incorrect. Please try again.")
            return redirect("/login")

        else:
            session["user_id"] = user_infor[0]["id"]
            return redirect("/")
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        email = request.form.get("email")

        if not username or not password or not confirmation or not email:
            flash("Please enter your username and password and confirmation and email")
            return redirect("/register")
        if password != confirmation:
            flash("The password and confirmation is not the same")
            return redirect("/register")

        try:
            db.execute("INSERT INTO users (name, password, email) VALUES (?,?,?)", username, generate_password_hash(password), email)
            return redirect("/")
        except:
            flash("The account is already exsist, please try other user name")
            return redirect("/register")
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/quote")
def quote():
    current_id = session["user_id"]
    quotes = db.execute("SELECT quote FROM quotes WHERE user_id=?", current_id)
    return render_template("quote.html", quotes = quotes)

@app.route("/edit", methods = ["GET", "POST"])
def edit():
    current_id= session["user_id"]
    id = None
    if request.method == "GET":
        quote1 = request.args.get("quote")
        id = db.execute("SELECT id FROM quotes where user_id=? AND quote =?", current_id, quote1)[0]["id"]
        return render_template("edit.html", quote = quote1, id = id)
    else:
        quote_changed = request.form.get("quote_changed")
        id = request.form.get("id") # Retrieve the original quote value
        if not quote_changed:
            flask("You need to give the quote")
            return redirect("/")
        db.execute("UPDATE quotes SET quote = ? WHERE user_id = ? AND id = ?", quote_changed, current_id, id)

        quotes = db.execute("SELECT quote FROM quotes WHERE user_id=?", current_id)
        return render_template("quote.html", quotes = quotes)

@app.route("/delete", methods = ["POST"] )
def delete():
    if request.method == "POST":
        current_id = session["user_id"]
        quote = request.form.get("quote")
        db.execute("DELETE FROM quotes WHERE quote = ? AND user_id =?", quote, current_id)

        quotes = db.execute("SELECT quote FROM quotes WHERE user_id=?", current_id)
        return render_template("quote.html", quotes = quotes)

def get_random_quote():
    current_id = session["user_id"]
    quotes = db.execute("SELECT quote FROM quotes WHERE user_id=?", current_id)
    random_quote = random.choice(quotes)
    return random_quote
@app.route("/send_email", methods=["POST"])
def send_email():
    if request.method == "POST":
        current_id = session["user_id"]
        email = db.execute("SELECT email FROM users WHERE id = ?", current_id)[0]['email']
        random_quote = get_random_quote()
        msg = Message(subject='Your Quote Today', recipients=[email], sender='dungdodz@gmail.com')
        msg.body = random_quote['quote']
        mail.send(msg)
        return redirect("/")

print(flask.__version__)





