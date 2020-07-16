# database.py Database wrappers for jonapp2
# Author: Nate Sales
#
# This file provides safe wrappers for database operations.
# It may be imported and used anywhere in the main server file.

import base64
import bcrypt
import gridfs
import pymongo
import random
from bson.objectid import ObjectId


def random_string():
    return "".join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789") for i in range(32))


class JonAppDatabase:
    def __init__(self, mongo_uri):
        # Core datastores
        self.client = pymongo.MongoClient(mongo_uri)
        self.db = self.client["jonapp2"]
        self.gridfs = gridfs.GridFS(self.db)

        # Collections
        self.supervisors = self.db["supervisors"]
        self.projects = self.db["projects"]
        self.users = self.db["users"]

    def get_image(self, object_id):
        try:
            entry = self.gridfs.get(object_id)
        except gridfs.errors.NoFile:
            return None

        if entry.contentType.strip().split("/")[0] != "image":  # If not an image, delete it.
            self._gridfs.delete(object_id)
            return None

        return "data:" + entry.contentType + ";base64, " + base64.b64encode(entry.read()).decode()

    def put_image(self, image):
        if image and image.filename:
            try:
                extension = image.filename.split(".")[1]
            except IndexError:  # No extension
                return error("No image extension specified")
            else:
                if image.content_type.split("/")[0] == "image":
                    return self._gridfs.put(image, content_type=image.content_type, filename="image-" + random_filename() + "." + extension)
        else:
            return error("No image specified")

    def delete_image(self, string_id):
        return self._gridfs.delete(ObjectId(string_id))

    # Projects

    def create_project(self, name, description, image, user):
        self.projects.insert_one({
            "name": name,
            "description": description,
            "image": self.put_image(image),
            "users": [user],
            "tasks": []
        })

    def update_project(self, project_id, name, description, image):
        self.projects.update_one({'_id': ObjectId(project_id)}, {'$set': {
            "name": name,
            "description": description,
            "image": self.put_image(image),
        }})

    def delete_project(self, project_id, user):
        project_doc = self.projects.find_one({"_id": ObjectId(project_id)})

        if not project_doc:  # If project with project_id doesn't exist, no need to do anything.
            return
        else:  # If it does exit, delete it.
            if user in project_doc["users"]:
                project_image = project_doc["image"]

                if project_image:
                    self.delete_image(project_image)

                self.projects.delete_one({"_id": ObjectId(project)})

    # Tasks

    def add_task(self, project_id, name, description, image):
        if not self.projects.find_one({"_id": ObjectId(project_id)}):
            return "Project not found"  # TODO: Real error page

        self.projects.update_one({"_id": ObjectId(project)}, {"$push": {"tasks": {
            "name": name,
            "description": description,
            "image": self.put_image(image),
            "state": "Pending",
            "subtasks": []
        }}})

    def update_task(self, project_id, task, name, description, image):
        if not self.projects.find_one({"_id": ObjectId(project_id)}):
            return "Project not found"  # TODO: Real error page

        if image == 'none':
            self.projects.update_one({"_id": ObjectId(project)}, {"$set": {"tasks." + task: {  # Append the new task
                "name": name,
                "description": description,
            }}})
        else:
            self.projects.update_one({"_id": ObjectId(project)}, {"$set": {"tasks." + task: {
                "name": name,
                "description": description,
                "image": self.put_image(image),
            }}})

    def delete_task(self, project_id, task_id):
        print("Deleting index " + str(task_id) + " from " + project_id)

        project_list = self.projects.find_one({"_id": ObjectId(project_id)})["tasks"]
        if project_list:
            del project_list[int(task_id)]
            self.projects.update_one({"_id": ObjectId(project_id)}, {"$set": {"tasks": project_list}})

    # Authentication

    def signup(self, email, name, password, type):
        if self.users.find_one({"email": email}):  # If account already exists
            return True  # Account already exists

        self.users.insert_one({
            "email": email,
            "name": name,
            "password": bcrypt.hashpw(password.encode(), bcrypt.gensalt()),
            "type": type
        })

        return False  # Account doesn't already exist

    def login(self, email, password):
        user_doc = self.users.find_one({"email": email})

        if user_doc and bcrypt.checkpw(password.encode(), user_doc["password"]):
            token = random_string()
            self.users.update_one(user_doc, {"$push": {"tokens": token}})
            return token
        else:
            return None

    def get_user(self, id):
        return self.users.find_one({"_id": ObjectId(id)})

    def is_authorized(self, project, user):
        return str(user) in self.projects.find_one({"_id": ObjectId(project)})["users"]

    # Getters

    def get_projects_html(self, user):
        projects = self.projects.find()
        for project in projects:
            if user in project["users"]:
                id = str(project["_id"])
                name = project["name"]
                description = project["description"]
                image = self.get_image(project["image"])

    def get_tasks_html(self, project_id):
        project_document = self.projects.find_one({"_id": ObjectId(project_id)})
        tasks_html = ""

        task_counter = 0
        for task in project_document["tasks"]:
            pass
