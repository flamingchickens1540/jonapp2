# database.py Database wrappers for jonapp2
# Author: Nate Sales
#
# This file provides safe wrappers for database operations.
# It may be imported anywhere in the main server file.

import gridfs
import pymongo
from bson.objectid import ObjectId

import bcrypt

import base64
import utils

import random
import string

import validators as valid


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

    def get_image(self, object_id):
        try:
            entry = self._gridfs.get(object_id)
        except gridfs.errors.NoFile:
            return "https://cdn.discordapp.com/attachments/473705436793798676/696918972771074068/Untitled_drawing_3.png"

        content_type = entry.contentType.strip()

        if content_type.split("/")[0] != "image":
            return "https://cdn.discordapp.com/attachments/473705436793798676/696918972771074068/Untitled_drawing_3.png"

        content = entry.read()
        return "data:" + content_type + ";base64, " + base64.b64encode(content).decode()

    def put_image(self, image):  # TODO: content_type checking
        if image and image.filename:
            try:
                extension = image.filename.split(".")[1]
            except IndexError:  # No extension
                return ""
            else:
                if image.content_type.split("/")[0] == "image":
                    return self._gridfs.put(image, content_type=image.content_type, filename="image-" + "".join(random.choice(string.ascii_lowercase) for i in range(32)) + "." + extension)
        else:
            return ""

    def delete_image(self, string_id):
        return self._gridfs.delete(ObjectId(string_id))

    def add_project(self, name, description, image):
        self.projects.insert_one({
            "name": name,
            "description": description,
            "image": self.put_image(image),
            "users": [],
            "tasks": []
        })

    def delete_project(self, project):
        project_doc = self.projects.find_one({"_id": ObjectId(project)})

        if not project_doc:
            return
        else:
            project_image = project_doc["image"]

            if project_image:
                self.delete_image(project_image)

        self.projects.delete_one({"_id": ObjectId(project)})

    def add_task(self, project, name, description, image):
        if not self.projects.find_one({"_id": ObjectId(project)}):
            return "Project not found"  # TODO: Real error page

        self.projects.update_one({"_id": ObjectId(project)}, {"$push": {"tasks": {
            "name": name,
            "description": description,
            "image": self.put_image(image),
            "state": "Pending",
            "subtasks": []
        }}})

    def register(self, email, password, role="Supervisor"):
        self.users.insert_one({
            "email": email,
            "hash": bcrypt.hashpw(password.encode(), self.salt.encode()),
            "role": role
        })

    def login(self, email, password):
        user_doc = self.users.find_one({"email": email})

        if user_doc:  # If account exists
            return user_doc["password_hash"] == password  # TODO: IMPORTANT! Hash the password with bcrypt!

    def get_projects_html(self, user):
        projects_html = ""

        projects = self.projects.find({})
        for project in projects:
            # if user in project["users"]:
            if True:
                id = str(project["_id"])
                name = project["name"]
                description = project["description"]
                image = self.get_image(project["image"])

                projects_html += """
                    <div class="col s12 m6 l4">
                        <div class="card hoverable">
                            <div class="card-image">
                            <img class="activator fit-to" src='""" + image + """'>
                            </div>
                            <div class="card-content">
                            <span class="card-title activator grey-text text-darken-4">""" + name + """</span>
                            <i class="material-icons right dropdown-trigger" data-target='dropdown-""" + id + """'>more_vert</i>
                            <p>""" + description[:16] + """</p>
                            </div>
                            <div class="card-reveal">
                            <span class="card-title grey-text text-darken-4">""" + name + """<i class="material-icons right">close</i></span>
                            <p>""" + description + """</p>
                            </div>
                        </div>
                        
                        <ul id='dropdown-""" + id + """' class='dropdown-content'>
                            <li><a href='/project/delete/""" + id + """'><i class="material-icons">delete</i>Delete</a></li>
                        </ul>
                        
                    </div>"""

        return projects_html

    # def add_supervisor(self, name, email):
    #     if not valid.email(email):
    #         raise ValueError("Invalid email in add_supervisor")
    #
    #     return str(self.supervisors.insert_one({
    #         "name": name,
    #         "email": email
    #     }).inserted_id)
    #
    # def add_user(self, name, supervisor):
    #     return str(self.users.insert_one({
    #         "name": name,
    #         "supervisors": [supervisor],
    #         "projects": []
    #     }).inserted_id)
    #
    # def add_task(self, project, name, description, image):
    #     if not self.projects.find_one({"_id": ObjectId(project)}):
    #         raise ValueError("Project id: " + project + " not found.")
    #
    #     self.projects.update_one({"_id": ObjectId(project)}, {"$push": {"tasks": {
    #         "name": name,
    #         "description": description,
    #         "image": self.put_image(image),
    #         "state": State.PENDING,
    #         "subtasks": []
    #     }}})

    # def login(self, email, password):
    #     userdoc = self.users.find_one({"email": email})
    #
    #     if userdoc:
    #         return bcrypt.checkpw(password.encode(), userdoc["hash"])
    #     else:
    #         return False

    # database.register("nate@nate.to", "mypassword")

    # print(database.login("nate@nate.to", "mypass1word"))

    # database.add_project("My project", "project dscr", "")
    # database.add_task("5e6130ca53074c9fe1e5e6d6", "Project Name", "Project descr", "")
