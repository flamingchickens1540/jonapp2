#!/usr/bin/python3
# main.py

from flask import (
    Flask,
    request,
    render_template,
    Markup
)

from database import JonAppDatabase
from utils import qr

HOST = "127.0.0.1"
PORT = 5001
PRODUCTION = False
VERSION = "0.1"

SUCCESS = "Operation completed successfully."

app = Flask(__name__)
database = JonAppDatabase("mongodb://10.255.70.10:5000/")


@app.route("/")
def index():
    return render_template("index.html")


# <supervisor>

@app.route("/supervisor/home")
def supervisor_home():
    return render_template("supervisor/home.html",
                           user_name="Nate Sales",
                           user_id="5e2cbf1c3246741b67f9201a",
                           user_email="nate@nate.to",
                           user_qr=Markup(qr("test"))
                           )


@app.route("/supervisor/project", methods=["GET"])
def supervisor_project():
    id = request.args.get("id")

    return render_template("supervisor/project.html",
                           project_name="My project",
                           tasks_html=Markup(database.get_tasks_html(id))
                           )


# </supervisor>


@app.route("/user/home")
def user_home():
    return render_template("user/home.html")


@app.route("/add/supervisor", methods=["POST"])
def add_supervisor():
    name = request.form["name"]
    email = request.form["email"]

    return database.add_supervisor(name, email)


@app.route("/add/user", methods=["POST"])
def add_user():
    name = request.form["name"]
    supervisor = request.form["supervisor"]

    return database.add_user(name, supervisor)


@app.route("/add/task", methods=["POST"])
def add_task():
    project = request.form["project"]
    name = request.form["name"]
    description = request.form["description"]
    image = request.files["image"]

    return database.add_task(project, name, description, image)


@app.route("/get/tasks", methods=["POST"])
def get_tasks():
    user = request.form["user"]

    return database.get_tasks(user)


@app.route("/add/project", methods=["POST"])
def add_project():
    name = request.form["name"]
    description = request.form["description"]

    return database.add_project(name, description)


app.run(host=HOST, port=PORT, debug=not PRODUCTION)
