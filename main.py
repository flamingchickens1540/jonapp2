#!/usr/bin/python3
# main.py

import os
from flask import Flask, request, render_template, Markup, redirect, session

from database import JonAppDatabase
from utils import *

HOST = "0.0.0.0"
PORT = 5001
PRODUCTION = False

app = Flask(__name__)
app.secret_key = os.urandom(64)
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

    user = database.get_user(id)
    return render_template("supervisor/home.html",
                           user_name="To be implemented",
                           user_id=session["id"],
                           user_email=user["email"],
                           user_qr=Markup(qr(session["id"])),
                           projects_html=Markup(database.get_projects_html(session["id"]))
                           )


@app.route("/add/project", methods=["POST"])
def add_project():
    if not authenticated(): return redirect("/supervisor/login")

    name = request.form["name"]
    description = request.form["description"]
    image = request.files["image"]

    database.add_project(name, description, image, id)
    return redirect("/projects")


@app.route("/update/project/<project>", methods=["POST"])
def update_project(project):
    if not authenticated(): return redirect("/supervisor/login")

    name = request.form["name"]
    description = request.form["description"]
    image = request.files["image"]

    database.update_project(name, description, image, project)
    return redirect("/projects")


@app.route("/logout")
def logout():
    del session["id"]
    return redirect("/")


# Auth

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
    if not authenticated(): return redirect("/supervisor/login")

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


@app.route("/project/delete/<path:project>")
def route_project_delete(project):
    if not authenticated(): return redirect("/supervisor/login")

    database.delete_project(project, id)
    return redirect("/projects")


# View, edit, or delete a project
@app.route("/project/<path:project>", methods=["GET", "POST", "DELETE"])
def project(pid):
    if not authenticated(): return redirect("/supervisor/login")

    if database.isAuthorized(project, id):  # TODO: Catch BSON InvalidId error in database
        return render_template("/supervisor/tasks.html", tasks=Markup(database.get_tasks_html(pid)))
    else:
        return redirect("/supervisor/login")


@app.route("/project/<path:project>/<path:task>/<path:method>", methods=["GET"])
def route_project_delete2(project, task, method):
    if not authenticated(): return redirect("/supervisor/login")

    project = project.strip("/")
    if database.isAuthorized(project, id):  # TODO: Catch BSON InvalidId error in database
        if method == "delete":
            database.delete_task(project, task)
            return redirect("/project/" + project)
        elif method == 'update':
            database.update_task(project, task)
            return redirect("/project/" + project)

    else:
        return redirect("/supervisor/login")


app.run(host=HOST, port=PORT, debug=not PRODUCTION)
