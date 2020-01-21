#!/usr/bin/python3
# main.py

from flask import (
    Flask,
    request,
    render_template,
    make_response,
    Markup
)

from time import time

PRODUCTION = False
VERSION = "0.1"

app = Flask(__name__)


@app.route("/api/alive")
def api_alive():
    return "JonApp API " + VERSION


@app.route("/api/task/add", methods=["POST"])
def api_task_add():
    try:
        name = request.form["name"]
        description = request.form["description"]
        image = request.form["image"]  # TODO: request.file?
    except KeyError:
        return "ERROR: Incorrect request structure", 200  # TODO: What error code?


app.run(host="127.0.0.1", port=5000, debug=not PRODUCTION)
