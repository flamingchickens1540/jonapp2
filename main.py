#!/usr/bin/python3
# main.py

from bson import ObjectId
from flask import (
    Flask,
    request,
    render_template
)

from database import JonAppDatabase

HOST = "127.0.0.1"
PORT = 5001
GLOBALURI = "http://" + HOST + ":" + str(PORT)  # No trailing '/'
PRODUCTION = False
VERSION = "0.1"

SUCCESS = "Operation completed successfully."

app = Flask(__name__, template_folder="templates/", static_folder="static/")
database = JonAppDatabase("mongodb://10.255.70.10:5000/")


@app.route("/ui/add/supervisor")
def ui_add_supervisor():
    return render_template("add_supervisor.html", GLOBALURI=GLOBALURI)


@app.route("/ui/add/user")
def ui_add_user():
    return render_template("add_user.html", GLOBALURI=GLOBALURI)


@app.route("/ui/add/task")
def ui_add_task():
    return render_template("add_task.html", GLOBALURI=GLOBALURI)


@app.route("/ui/get/tasks")
def ui_get_tasks():
    return render_template("get_tasks.html", GLOBALURI=GLOBALURI)


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
    user = request.form["user"]
    name = request.form["name"]
    desc = request.form["desc"]
    image = request.files["image"]

    database.add_task(user, name, desc, image)
    return SUCCESS


@app.route("/get/tasks", methods=["POST"])
def get_tasks():
    user = request.form["user"]

    return str(database.get_tasks(user))


app.run(host=HOST, port=PORT, debug=not PRODUCTION)
