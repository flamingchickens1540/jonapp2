#!/usr/bin/python3
# main.py

from flask import Flask, request, render_template, Markup, redirect, session

from database import JonAppDatabase
from utils import *

import os

HOST = "127.0.0.1"
PORT = 5001
PRODUCTION = False

app = Flask(__name__)
app.secret_key = os.urandom(64)
database = JonAppDatabase("mongodb://app1.srv.pdx1.nate.to:7000/")


@app.route("/")
def index():
    return render_template("index.html", user_name="Seth Knights")


# <supervisor>

@app.route("/supervisor/home")
def supervisor_home():
    try:
        id = session["id"]
        if not id:
            return redirect("/supervisor/login")
    except KeyError:
        return redirect("/supervisor/login")

    user = database.get_user(id)
    return render_template("supervisor/home.html",
                           user_name="To be implemented",
                           user_id=session["id"],
                           user_email=user["email"],
                           user_qr=Markup(qr(session["id"])),
                           projects_html=Markup(database.get_projects_html(session["id"]))
                           )


# </supervisor>


@app.route("/add/project", methods=["POST"])
def add_project():
    try:
        id = session["id"]
        if not id:
            return redirect("/supervisor/login")
    except KeyError:
        return redirect("/supervisor/login")

    name = request.form["name"]
    description = request.form["description"]
    image = request.files["image"]

    database.add_project(name, description, image, id)
    return redirect("/supervisor/home")


@app.route("/signup")
def signup():
    return render_template("/supervisor/signup.html")


@app.route("/logout")
def logout():
    del session["id"]
    return redirect("/")


@app.route("/project/delete", defaults={"project": ""})
@app.route("/project/delete/<path:project>")
def route_project_delete(project):
    try:
        id = session["id"]
        if not id:
            return redirect("/supervisor/login")
    except KeyError:
        return redirect("/supervisor/login")

    database.delete_project(project, id)
    return redirect("/supervisor/home")


# Auth

@app.route("/signup", methods=["GET", "POST"])
def route_signup():
    if request.method == "GET":
        return render_template("/supervisor/signup.html")

    elif request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if email and password:
            if database.signup(email, password):
                return redirect("/supervisor/login")
            else:
                return "An account with this email already exists."
        else:
            return "You may not leave the username or password field blank."


@app.route("/supervisor/login", methods=["GET", "POST"])
def route_login():
    try:
        if session["id"]:
            return redirect("/supervisor/home")
    except KeyError:
        pass

    if request.method == "GET":
        return render_template("/supervisor/login.html")

    elif request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        id = database.login(email, password)
        if id:
            session["id"] = id
            return redirect("/supervisor/home")
        else:
            return "Invalid username or password"


@app.route("/project", defaults={"project": ""})
@app.route("/project/<path:project>", methods=["GET", "POST"])
def route_project(project):
    try:
        id = session["id"]
        if not id:
            return redirect("/supervisor/login")
    except KeyError:
        return redirect("/supervisor/login")

    if database.isAuthorized(project, id):
        if request.method == "POST":
            name = request.form["name"]
            description = request.form["description"]
            image = request.files["image"]

            database.add_task(project, name, description, image)

        proj = database.get_tasks_html(project)
        return render_template("/supervisor/tasks.html", tasks=Markup(proj))
    else:
        return redirect("/supervisor/login")


# End auth


app.run(host=HOST, port=PORT, debug=not PRODUCTION)
