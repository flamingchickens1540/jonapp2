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

        if entry.contentType.strip().split("/")[0] != "image":  # If not an image
            return "https://cdn.discordapp.com/attachments/473705436793798676/696918972771074068/Untitled_drawing_3.png"

        content = entry.read()
        return "data:" + entry.contentType + ";base64, " + base64.b64encode(content).decode()

    def put_image(self, image):  # TODO: content_type checking
        if image and image.filename:
            try:
                extension = image.filename.split(".")[1]
            except IndexError:  # No extension
                return ""
            else:
                if image.content_type.split("/")[0] == "image":
                    return self._gridfs.put(image, content_type=image.content_type, filename="image-" + "".join(
                        random.choice(string.ascii_lowercase) for i in range(32)) + "." + extension)
        else:
            return ""

    def delete_image(self, string_id):
        return self._gridfs.delete(ObjectId(string_id))

    def add_project(self, name, description, image, user):
        self.projects.insert_one({
            "name": name,
            "description": description,
            "image": self.put_image(image),
            "users": [user],
            "tasks": []
        })

    def delete_project(self, project, user):
        project_doc = self.projects.find_one({"_id": ObjectId(project)})

        if not project_doc:
            return
        else:
            if user in project_doc["users"]:
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

    def signup(self, email, password):
        if self.users.find_one({"email": email}):  # If account already exists
            return False

        self.users.insert_one({
            "email": email,
            "password": bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        })

        return True

    def login(self, email, password):
        user_doc = self.users.find_one({"email": email})

        if user_doc and bcrypt.checkpw(password.encode(), user_doc["password"]):
            return str(user_doc["_id"])
        else:
            return None

    def get_user(self, id):
        return self.users.find_one({"_id": ObjectId(id)})

    def delete_task(self, project_id, task_id):
        print("Deleting index " + str(task_id) + " from " + project_id)

        project_list = self.projects.find_one({"_id": ObjectId(project_id)})["tasks"]
        if project_list:
            del project_list[int(task_id)]
            self.projects.update_one({"_id": ObjectId(project_id)}, {"$set" : {"tasks": project_list}})

    def get_projects_html(self, user):
        projects_html = ""

        projects = self.projects.find({})
        for project in projects:
            if user in project["users"]:
                id = str(project["_id"])
                name = project["name"]
                description = project["description"]
                image = self.get_image(project["image"])

                projects_html += """
                    <div class="col s12 m6 l4">
                        <div class="card hoverable">
                            <div class="card-image">
                            <img onclick="window.location='/project/""" + id + """'" class="fit-to" src='""" + image + """'>
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

    def get_tasks_html(self, project_id):
        project_document = self.projects.find_one({"_id": ObjectId(project_id)})
        tasks_html = ""

        task_counter = 0
        for task in project_document["tasks"]:
            tasks_html += """
            <li class="default" id='task""" + str(task_counter) + """'>
                <div class="row">
                    <div class="col s12 m12 l12">
                        <div class="card-panel task white">
                            <div class="row valign-wrapper no-bottom-margin">
                                <div class="col s3 m3 l2 valign-wrapper">
                                    <img class="task-preview-img" src='""" + self.get_image(task["image"]) + """'>
                                </div>
                                <div class="col s8 m8 l9">
                                    <span class="task-title">""" + task["name"] + """ #<span id="num"></span></span>
                                    <p class="task-desc grey-text text-darken-2">""" + task["description"] + """</p>
                                </div>
                                <div class="col s1 m1 l1 valign-wrapper">
                                    <i class="material-icons dropdown-trigger" data-target="dropdown""" + str(task_counter) + """">more_vert</i>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </li>
            
        <ul id="dropdown""" + str(task_counter) + """" class="dropdown-content">
        <li><a href='""" + str(task_counter) + """/delete'><i class="material-icons">delete</i>Delete</a></li>
        </ul>"""

            task_counter += 1

        return tasks_html

    def isAuthorized(self, project, user):
        return str(user) in self.projects.find_one({"_id": ObjectId(project)})["users"]
