#!/usr/bin/python3
# main.py

from flask import Flask, request, render_template, Markup, redirect, session

from database import JonAppDatabase
from utils import *

HOST = "0.0.0.0"
PORT = 5001
PRODUCTION = False

app = Flask(__name__)
app.secret_key = b'13568888'  # os.urandom(64)
database = JonAppDatabase("mongodb://inventeam.catlin.edu:4497/")


# Is a user authenticated?
def authenticated():
    try:
        id = session["id"]
        if not id:
            raise KeyError  # Cause an exception to be caught below
    except KeyError:
        return False
    else:
        return True


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/projects")
def supervisor_home():
    if not authenticated(): return redirect("/supervisor/login")

    user = database.get_user(session["id"])
    return render_template("supervisor/home.html",
                           user_name="To be implemented",
                           user_id=session["id"],
                           user_email=user["email"],
                           user_qr=Markup(qr(session["id"])),
                           projects_html=Markup(database.get_projects_html(session["id"]))
                           )


@app.route("/signup", methods=["GET", "POST"])
def route_signup():
    if request.method == "GET":
        return render_template("/supervisor/signup.html")

    elif request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if not email and password: return "You may not leave the username or password field blank."

        if database.signup(email, password):
            return redirect("/supervisor/login")
        else:
            return "An account with this email already exists."


@app.route("/supervisor/login", methods=["GET", "POST"])
def route_login():
    if authenticated(): return redirect("/projects")

    if request.method == "GET":
        return render_template("/supervisor/login.html")

    elif request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        id = database.login(email, password)
        if id:
            session["id"] = id
            return redirect("/projects")
        else:
            return "Invalid username or password"


@app.route("/logout")
def route_logout():
    del session["id"]
    return redirect("/")


# Create a project
@app.route("/create/project", methods=["POST"])
def add_project():
    if not authenticated(): return redirect("/supervisor/login")

    name = request.form["name"]
    description = request.form["description"]
    image = request.files["image"]

    database.add_project(name, description, image, session["id"])
    return redirect("/projects")


# View, edit, or delete a project
@app.route("/project/<path:project>/", methods=["GET", "POST", "DELETE"])
def route_project(project):
    if not authenticated(): return redirect("/supervisor/login")

    if database.isAuthorized(project, session["id"]):  # TODO: Catch BSON InvalidId error in database
        if request.method == "GET":  # View the project
            return render_template("/supervisor/tasks.html", tasks=Markup(database.get_tasks_html(project)))
        elif request.method == "POST":  # Edit the project
            pass  # TODO: Process the editing here
        elif request.method == "DELETE":  # Delete the project
            pass  # TODO: Delete the project

        return redirect("/projects")

    else:
        return redirect("/supervisor/login")


# Create a project
@app.route("/create/task", methods=["POST"])
def route_create_task():
    if not authenticated(): return redirect("/supervisor/login")

    project = request.form["project"]
    name = request.form["name"]
    description = request.form["description"]
    image = request.files["image"]

    database.add_task(project, name, description, image)
    return redirect("/projects")

# Edit or delete a task
@app.route("/task/<path:project>/<path:task>/", methods=["POST", "DELETE"])
def route_task(project, task):
    if not authenticated(): return redirect("/supervisor/login")

    if database.isAuthorized(project, session["id"]):  # TODO: Catch BSON InvalidId error in database
        if request.method == "POST":  # Edit the task
            pass
        elif request.method == "DELETE":  # Delete the task
            pass
    else:
        return redirect("/supervisor/login")


app.run(host=HOST, port=PORT, debug=not PRODUCTION)
