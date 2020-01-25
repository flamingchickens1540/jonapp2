# database.py Database wrappers for jonapp2
# Author: Nate Sales
#
# This file provides safe wrappers for database operations.
# It may be imported anywhere in the main server file.

import base64
import json

import gridfs
import pymongo
from bson.objectid import ObjectId

import validators as valid


class JonAppDatabase:
    def __init__(self, mongo_uri):
        # Core datastores
        self._client = pymongo.MongoClient(mongo_uri)
        self._db = self._client["jonapp2"]
        self._gridfs = gridfs.GridFS(self._db)

        # Collections
        self._supervisors = self._db["supervisors"]
        self._users = self._db["users"]

    def get_image(self, object_id):  # TODO: No content_type checking. This should only allow images
        entry = self._gridfs.get(object_id)
        content_type = entry.contentType.strip()
        content = entry.read()
        return "<img src='data:" + content_type + ";base64, " + base64.b64encode(content).decode() + "'>"

    def delete_image(self, string_id):
        return self._gridfs.delete(ObjectId(string_id))

    def add_supervisor(self, name, email):
        if not valid.email(email):
            raise ValueError("Invalid email in add_supervisor")

        return str(self._supervisors.insert_one({
            "name": name,
            "email": email
        }).inserted_id)

    def add_user(self, name, supervisor):
        return str(self._users.insert_one({
            "name": name,
            "supervisors": [supervisor],
            "tasks": []
        }).inserted_id)

    def add_task(self, user, name, description, image):
        task = {
            "name": name,
            "description": description,
            "image": self._gridfs.put(image, content_type=image.content_type, filename=image.filename)
        }

        self._users.update_one({'_id': ObjectId(user)}, {'$push': {'tasks': task}})
        return user

    def get_tasks(self, string_id):
        tasks_raw = self._users.find_one({'_id': ObjectId(string_id)})["tasks"]
        tasks_arr = []

        for task in tasks_raw:
            tasks_arr.append({
                "name": task["name"],
                "description": task["description"],
                "image": self.get_image(task["image"])
            })

        return json.dumps(tasks_arr)
