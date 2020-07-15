#!/usr/bin/python3
# main.py

import json
import json
import os
from bson.errors import InvalidId
from bson.objectid import ObjectId
from flask import Flask, request, Response

from database import JonAppDatabase

HOST = "localhost"
PORT = 5001
PRODUCTION = (HOST != "localhost")

app = Flask(__name__)
app.secret_key = os.urandom(64)
database = JonAppDatabase("mongodb://inventeam.catlin.edu:4497/")

# TODO: Static typing in function parameters

defaults = {
    # HTTP 2xx
    200: "Operation completed successfully",
    201: "Object created successfully",

    # HTTP 4xx
    400: "Bad Request",
    403: "Forbidden",
    404: "Not Found",

    # HTTP 5xx
    500: "Internal Server Error",
    501: "Not Implemented"
}


def response(code, data=None):
    resp = {
        "message": defaults[code]
    }

    if data is not None:
        resp["data"] = data

    return Response(json.dumps(resp), status=code, mimetype="application/json")


# General routes

@app.route("/")
def index():
    return response(404)


# Authentication routes

@app.route("/login", methods=["POST"])
def route_login():
    if request.json is None:
        return response(400, "JSON payload must not be empty")

    try:
        email = request.json["email"]
        password = request.json["password"]
    except KeyError:
        return response(400, "Required argument email/password/ not found")

    token = database.login(email, password)
    if not token:
        return response(403, "Username or password is incorrect")

    return response(200, token)


@app.route("/signup", methods=["POST"])
def route_signup():
    if request.json is None:
        return response(400, "JSON payload must not be empty")

    try:
        email = request.json["email"]
        password = request.json["password"]
        type = request.json["type"]
    except KeyError:
        return response(400, "Required argument email/password/type not found")

    if not (type == "supervisor" or type == "user"):
        print(type)
        return response(400, "Type must be either 'supervisor' or 'user'")

    account_exists = database.signup(email, password, type)
    if account_exists:
        return response(400, "Account with this email already exists")

    return response(201)


# Project routes

@app.route("/projects", methods=["POST"])
def projects():
    return response(501)


@app.route("/project/create", methods=["POST"])
def project_create():
    name = request.form.get("name")
    description = request.form.get("description")
    image = request.files.get("image")

    if name is None or description is None or image is None:
        return response(400, "Required argument name/description/image must not be none")

    return response(501)


@app.route("/project", methods=["GET", "POST", "DELETE"])
def project():
    project_id = request.args.get("id")

    if project_id is None:
        return response(400, "Required URL parameter id must not be none")

    try:
        garbage = ObjectId(project_id)
    except InvalidId:  # Reject bad ObjectIds
        return response(400, "URL parameter isn't a valid ID")

    if request.method == "GET":
        return response(501)
    elif request.method == "POST":
        return response(501)
    elif request.method == "DELETE":
        return response(501)


# Task routes

@app.route("/task/create", methods=["POST"])
def task_create():
    name = request.form.get("name")
    description = request.form.get("description")
    image = request.files.get("image")
    project_id = request.form.get("project-id")

    if name is None or description is None or image is None:
        return response(400, "Required argument name/description/image/project_id must not be none")

    return response(501)


app.run(host=HOST, port=PORT, debug=not PRODUCTION)
