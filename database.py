# database.py Database wrappers for jonapp2
# Author: Nate Sales
#
# This file provides safe wrappers for database operations.
# It may be imported anywhere in the main server file.

import base64

import gridfs
import pymongo
from bson.objectid import ObjectId

import bcrypt

import validators as valid


class State:
    PENDING = 1
    PROBLEM = 2
    COMPLETE = 3


class Role:
    SUPERVISOR = 1
    USER = 2
    ADMIN = 3


class JonAppDatabase:
    def __init__(self, mongo_uri):
        # Core datastores
        self._client = pymongo.MongoClient(mongo_uri)
        self._db = self._client["jonapp2"]
        self._gridfs = gridfs.GridFS(self._db)

        # Collections
        self.supervisors = self._db["supervisors"]
        self.projects = self._db["projects"]
        self.users = self._db["users"]

        self.salt = "$2b$12$MfET9FATeW4fyP3f3OInGe"

    def get_image(self, object_id):  # TODO: No content_type checking. This should only allow images
        entry = self._gridfs.get(object_id)
        content_type = entry.contentType.strip()

        if content_type.split("/")[0] != "image":
            raise ValueError("Content type " + content_type + " not supported.")

        content = entry.read()
        return "data:" + content_type + ";base64, " + base64.b64encode(content).decode()

    def put_image(self, image):
        if image:
            return self._gridfs.put(image, content_type=image.content_type, filename=image.filename)
        else:
            return ""

    def delete_image(self, string_id):
        return self._gridfs.delete(ObjectId(string_id))

    def add_supervisor(self, name, email):
        if not valid.email(email):
            raise ValueError("Invalid email in add_supervisor")

        return str(self.supervisors.insert_one({
            "name": name,
            "email": email
        }).inserted_id)

    def add_user(self, name, supervisor):
        return str(self.users.insert_one({
            "name": name,
            "supervisors": [supervisor],
            "projects": []
        }).inserted_id)

    def add_project(self, name, description, image):
        return str(self.projects.insert_one({
            "name": name,
            "description": description,
            "image": self.put_image(image),
            "users": [],
            "tasks": []
        }).inserted_id)

    def add_task(self, project, name, description, image):
        if not self.projects.find_one({"_id": ObjectId(project)}):
            raise ValueError("Project id: " + project + " not found.")

        self.projects.update_one({"_id": ObjectId(project)}, {"$push": {"tasks": {
            "name": name,
            "description": description,
            "image": self.put_image(image),
            "state": State.PENDING,
            "subtasks": []
        }}})

    def get_tasks_html(self, project):
        tasks_html = ""

        tasks = self.projects.find_one({"_id": ObjectId(project)})["tasks"]
        for task in tasks:
            task = self._tasks.find_one({"_id": ObjectId(task)})

            id = str(task["_id"])
            name = task["name"]
            description = task["description"]
            image = self.get_image(task["image"])

            tasks_html += """
                    <tr>
                        <td class="align-middle" onclick="$('.collapse_""" + id + """').collapse('toggle')">
                            <div class="panel-group" id="accordion">
                                <div class="panel panel-default">
                                    <div class="panel-heading">
                                        <h5 class="panel-title mb-0">""" + name + """</h5>
                                    </div>
                                    <div class="panel-collapse collapse in collapse_project1">
                                        <div class="panel-body">
                                            <p>""" + description + """</p>
    
                                            <div class="container">
                                                <img alt="Project Image" class="img-fluid p-4" src=""" + image + """>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </td>
    
                        <td class="align-middle">
                            <button class="btn btn-danger" onclick="$('#projectEditModal').modal();" type="button">Edit
                            </button>
                        </td>
                   </tr>"""

        return tasks_html

    def register(self, email, password, role=Role.SUPERVISOR):
        self.users.insert_one({
            "email": email,
            "hash": bcrypt.hashpw(password.encode(), self.salt.encode()),
            "role": role
        })

    def login(self, email, password):
        userdoc = self.users.find_one({"email": email})

        if userdoc:
            return bcrypt.checkpw(password.encode(), userdoc["hash"])
        else:
            return False

# database.register("nate@nate.to", "mypassword")

# print(database.login("nate@nate.to", "mypass1word"))

# database.add_project("My project", "project dscr", "")
# database.add_task("5e6130ca53074c9fe1e5e6d6", "Project Name", "Project descr", "")
