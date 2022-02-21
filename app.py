import os
import datetime
import re

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from helpers import login_required, allowed_file

UPLOAD_FOLDER = 'static/img/babypics'


# Configure application
app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = 'filesystem'
Session(app)



# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

db = SQL("sqlite:///babylove.db")

@app.route("/")
def index():
    # check if user is logged in, if not direct them to the spash page to explain Babylove, if logged in direct them to their dashboard
    if not session:
        return render_template("index.html")
    else:
        return redirect("/home")
        

@app.route("/register", methods=["GET", "POST"])
def register():
    # show register form
    if request.method == "GET":
        return render_template("register.html")
    # process registry
    if request.method == "POST":
        # get user input
        name = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        # make sure user input's details
        if not name:
            flash("Please input username")
            return redirect("/register")
        if not password:
            flash("Please input password ")
            return redirect("/register")
        if not password == confirmation:
            flash("Passwords do not match")
            return redirect("/register")
        # check if username is already in use
        namecheck = db.execute("SELECT username FROM users WHERE username=?", (name, ))
        if not namecheck == []:
            flash("Username already exists, please try again")
            return redirect("/register")
        # check password complexicity
        if len(password) < 8 or not re.search("[a-z]", password) or not re.search("[A-Z]", password) or not re.search("[0-9]", password):
            flash ("- Please enter password over 8 characters, including both upper and lower case letters, and at least one number")
            return redirect("/register")
        # hash password and enter details into database
        else:
            hashed = generate_password_hash(password)
            db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", name, hashed)
        return redirect("/")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Must provide username")
            return redirect("/login")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Must provide password")
            return redirect("/login")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Invalid username and/or password")
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/home")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    # show add child form
    if request.method == "GET":
        return render_template("add.html")
    # process add child information
    else:
        # get user input
        babyname = request.form.get("name")
        birthday = request.form.get("birthday")
        sex = request.form.get("sex")
        # check form is filled out
        if not babyname or not birthday or not sex:
            flash("- Please add name and DOB and sex")
            return redirect("/add")
        # check if user has a baby of the same name
        namecheck = db.execute("SELECT babyname FROM babies WHERE babyname=? AND id IN(SELECT baby_id FROM families WHERE parent_id=?)", babyname, session["user_id"])
        if not namecheck == []:
            flash("- Sorry this babyname already exists. Please add different name.")
            return redirect("/add")
        file = request.files['file']
        # Check if user added picture, inform them default picture will be used
        if 'file' not in request.files or file.filename == '':
            babyid = db.execute("INSERT INTO babies (babyname, birthday, sex) VALUES(?, ?, ?)", babyname, birthday, sex)
            db.execute("INSERT INTO families (parent_id, baby_id) VALUES (?, ?)", session["user_id"], babyid)
            flash('Baby added successfully, but no picture added. Default picture used')
            return redirect("/home")
        # check picture file is in accepted format
        elif not allowed_file(file.filename):
            flash('Picture not accepted format, please try again')
            return redirect("/add")
        filename = secure_filename(file.filename)
        # check that file doesn't already exist
        filecheck = db.execute("SELECT photo FROM babies WHERE photo=?", filename)
        if not filecheck == []:
            flash("- Sorry this filename already exists. Please rename, or add a different file")
            return redirect("/add")
        # insert baby into database
        babyid = db.execute("INSERT INTO babies (babyname, birthday, sex) VALUES(?, ?, ?)", babyname, birthday, sex)
        db.execute("INSERT INTO families (parent_id, baby_id) VALUES (?, ?)", session["user_id"], babyid)
        # add picture to babypics directory and save location in database
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        db.execute("UPDATE babies SET photo=? WHERE id=?", filename, babyid)
        return redirect("/home")



@app.route("/track", methods=["GET", "POST"])
@login_required
def track():
    # show initial track form
    if request.method == "GET":
        # Get the babies registered to this user
        babies = db.execute("SELECT babyname FROM babies WHERE id IN(SELECT baby_id FROM families WHERE parent_id=?)", session["user_id"])
        # check that the user has added their baby, and if not direct them to the add baby page
        if babies == []:
            flash("Please add a baby")
            return redirect("/add")
        else:
            return render_template("track.html", babies=babies)
    else:
        # collect user input
        feed = request.form.get("feed")
        sleep = request.form.get("sleep")
        nappy = request.form.get("nappy")
        baby = request.form.get("baby")
        # check that they picked a baby
        if baby is None:
            flash("Please pick a babyname!")
            return redirect("/track")
        # set up start time of tracked activity
        dates = datetime.datetime.now()
        date = datetime.date.today()
        time = dates.strftime("%H:%M")
        # direct to appropriate tracking page for activity wanted
        if feed is not None:
            return render_template("feed.html", baby=baby, date=date, time=time)
        if sleep is not None:
            return render_template("sleep.html", baby=baby, date=date, time=time)
        if nappy is not None:
            return render_template("nappy.html", baby=baby, date=date, time=time)

@app.route("/activity", methods=["POST"])
@login_required
def activity():
    # get user input
    left = request.form.get("left")
    right = request.form.get("right")
    date = request.form.get("date")
    name = request.form.get("name")
    bottle = request.form.get("bottle")
    time = request.form.get("time")
    sleep = request.form.get("sleep")
    pee = request.form.get("pee")
    poop = request.form.get("poop")
    # check that there is a name for the baby
    if not name:
        flash("No babyname detected, please try again")
        return redirect("/track")
    # input data into activites table in database
    else:
        babyid = db.execute("SELECT id FROM babies WHERE id IN(SELECT baby_id FROM families WHERE parent_id=?) AND babies.babyname=?", session["user_id"], name)
        babyid = babyid[0]["id"]
        db.execute("INSERT INTO activities (baby_id, left, right, bottle, poo, pee, sleep, date, time) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", babyid, left, right, bottle, poop, pee, sleep, date, time)
        return redirect("/home")

@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    if request.method == "GET":
        babies = db.execute("SELECT * FROM babies WHERE id IN(SELECT baby_id FROM families WHERE parent_id=?)", session["user_id"])
        if babies == []:
            flash("Please add a baby to get started")
            return redirect("/add")
        else:
            dates = db.execute("SELECT DISTINCT date FROM activities WHERE baby_id IN(SELECT baby_id FROM families WHERE parent_id=?)", session["user_id"])
            name = babies[0]["babyname"]
            photo = babies[0]["photo"]
            babyid = babies[0]["id"]
            date = datetime.date.today()
            activities = db.execute("SELECT * FROM activities WHERE baby_id=? and date=? ORDER BY time DESC", babyid, date)
            return render_template("home.html", photo=photo, activities=activities, name=name, babies=babies, dates=dates, date=date)
    else:
        name = request.form.get("baby")
        date = request.form.get("date")
        if not name:
            flash("No name given")
            return redirect("/home")
        if not date:
            flash("No date given")
            return redirect("/home")
        babies = db.execute("SELECT * FROM babies WHERE id IN(SELECT baby_id FROM families WHERE parent_id=?)", session["user_id"])
        baby = db.execute("SELECT * FROM babies WHERE babyname=? AND id IN(SELECT baby_id FROM families WHERE parent_id=?)", name, session["user_id"])
        babyid = baby[0]["id"]
        dates = db.execute("SELECT DISTINCT date FROM activities WHERE baby_id IN(SELECT baby_id FROM families WHERE parent_id=?)", session["user_id"])    
        photo = baby[0]["photo"]
        if not photo:
            photo = "default.jfif"
        activities = db.execute("SELECT * FROM activities WHERE baby_id=? and date=? ORDER BY time DESC", babyid, date)
        return render_template("home.html", photo=photo, activities=activities, name=name, babies=babies, dates=dates, date=date)

