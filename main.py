#!/usr/bin/python3
# main.py

from flask import Flask, request, render_template, Markup, redirect

from database import JonAppDatabase
from utils import *

HOST = "127.0.0.1"
PORT = 5001
PRODUCTION = False

app = Flask(__name__)
database = JonAppDatabase("mongodb://app1.srv.pdx1.nate.to:7000/")

@app.route("/")
def index():
    return render_template("index.html", user_name="Seth Knights")


# <supervisor>

@app.route("/supervisor/home")
def supervisor_home():
    return render_template("supervisor/home.html",
                           user_name="Nate Sales",
                           user_id="5e2cbf1c3246741b67f9201a",
                           user_email="nate@nate.to",
                           user_qr=Markup(qr("test")),

                           projects_html=Markup(database.get_projects_html("nate"))
                           )


# </supervisor>


@app.route("/add/project", methods=["POST"])
def add_project():
    name = request.form["name"]
    description = request.form["description"]
    image = request.files["image"]

    database.add_project(name, description, image)
    return redirect("/supervisor/home")

@app.route("/signup")
def signup():
    return render_template("/supervisor/signup.html")


@app.route("/project/delete", defaults={"id": ""})
@app.route("/project/delete/<path:id>")
def route_project_delete(id):
    database.delete_project(id)
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
                return redirect("/login")
            else:
                return "An account with this email already exists."
        else:
            return "You may not leave the username or password field blank."


@app.route("/login", methods=["GET", "POST"])
def route_login():
    if request.method == "GET":
        return render_template("/supervisor/login.html")

    elif request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if database.login(email, password):
            return "Welcome"
        else:
            return "Invalid username or password"


# End auth


# @app.route("/user/home")
# def user_home():
#     return render_template("user/home.html")
#
#
# @app.route("/add/supervisor", methods=["POST"])
# def add_supervisor():
#     name = request.form["name"]
#     email = request.form["email"]
#
#     return database.add_supervisor(name, email)
#
#
# @app.route("/add/user", methods=["POST"])
# def add_user():
#     name = request.form["name"]
#     supervisor = request.form["supervisor"]
#
#     return database.add_user(name, supervisor)
#
#
# @app.route("/add/task", methods=["POST"])
# def add_task():
#     project = request.form["project"]
#     name = request.form["name"]
#     description = request.form["description"]
#     image = request.files["image"]
#
#     return database.add_task(project, name, description, image)
#
#
# @app.route("/get/tasks", methods=["POST"])
# def get_tasks():
#     user = request.form["user"]
#
#     return database.get_tasks(user)


app.run(host=HOST, port=PORT, debug=not PRODUCTION)
