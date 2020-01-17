# database.py Database wrappers for jonapp2
# Author: Nate Sales
#
# This file provides safe wrappers for database operations.
# It may be imported anywhere in the main server file.

import pymongo
from bson.objectid import ObjectId
from pymongo.binary import Binary

def initialize(mongoURI):
    global client, db, supervisors, users

    client = pymongo.MongoClient(mongoURI)
    db = client["jonapp2"]
    supervisors = db["supervisors"]
    users = db["users"]

def add_supervisor(name, email):
    return supervisors.insert_one({
        "name": name,
        "email": email
    }).inserted_id

def add_user(name, supervisor):
    return users.insert_one({
        "name": name,
        "supervisors": [supervisor],
        "tasks": []
    }).inserted_id

def add_task(user, name, description, image):
    task = {
        "name": name,
        "description": description,
        "image": Binary(image)
    }

    users.update_one({'_id': ObjectId(user)}, {'$push': {'tasks': task}})

initialize("mongodb://localhost:27017/")

# supervisor = add_supervisor("Nate1", "nate@natesales.net")
# user = add_user("Jon", supervisor)
# add_task(user, "Clean camera", "Clean the camera", "base64/image...")
add_task("5e2147e388cabc49cebf65a5", "Organize", "Ctest camera", "batestage...")