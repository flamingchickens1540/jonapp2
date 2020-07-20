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
import bson.errors
import bson.objectid


def random_string():
    return "".join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789") for i in range(32))


class JonAppDatabase:
    def __init__(self, mongo_uri: str):
        # Core datastores
        self.client = pymongo.MongoClient(mongo_uri)
        self.db = self.client["jonapp2"]
        self.gridfs = gridfs.GridFS(self.db)

        # Collections
        self.supervisors = self.db["supervisors"]
        self.projects = self.db["projects"]
        self.users = self.db["users"]

    def get_image(self, object_id: str):
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
                return "No image extension specified"
            else:
                if image.content_type.split("/")[0] == "image":
                    return self._gridfs.put(image, content_type=image.content_type, filename="image-" + random_filename() + "." + extension)
        else:
            return "No image specified"

    def delete_image(self, string_id):
        return self._gridfs.delete(bson.objectid.ObjectId(string_id))

    # Projects

    def create_project(self, name: str, description: str, image, user: str):
        # TODO: Type checking and error handling

        new_project = self.projects.insert_one({
            "name": name,
            "description": description,
            "image": image,  # TODO: replace with self.put_image(image),
            "users": [user]
        })

        self.users.update_one({"_id": user}, {"$push": {"projects": str(new_project.inserted_id)}})

    def update_project(self, project_id: str, name: str, description: str, image):
        self.projects.update_one({'_id': bson.objectid.ObjectId(project_id)}, {'$set': {
            "name": name,
            "description": description,
            "image": self.put_image(image),
        }})

    def delete_project(self, project_id: str, user: str):
        project_doc = self.projects.find_one({"_id": bson.objectid.ObjectId(project_id)})

        if not project_doc:  # If project with project_id doesn't exist, no need to do anything.
            return
        else:  # If it does exit, delete it.
            if user in project_doc["users"]:
                project_image = project_doc["image"]

                if project_image:
                    self.delete_image(project_image)

                self.projects.delete_one({"_id": bson.objectid.ObjectId(project)})

    # Tasks

    def add_task(self, project_id: str, name: str, description: str, image):
        if not self.projects.find_one({"_id": bson.objectid.ObjectId(project_id)}):
            return "Project not found"  # TODO: Real error page

        self.projects.update_one({"_id": bson.objectid.ObjectId(project)}, {"$push": {"tasks": {
            "name": name,
            "description": description,
            "image": self.put_image(image),
            "state": "Pending",
            "subtasks": []
        }}})

    def update_task(self, project_id: str, task: str, name: str, description: str, image):
        if not self.projects.find_one({"_id": bson.objectid.ObjectId(project_id)}):
            return "Project not found"  # TODO: Real error page

        if image == 'none':
            self.projects.update_one({"_id": bson.objectid.ObjectId(project)}, {"$set": {"tasks." + task: {  # Append the new task
                "name": name,
                "description": description,
            }}})
        else:
            self.projects.update_one({"_id": bson.objectid.ObjectId(project)}, {"$set": {"tasks." + task: {
                "name": name,
                "description": description,
                "image": self.put_image(image),
            }}})

    def delete_task(self, project_id, task_id):
        print("Deleting index " + str(task_id) + " from " + project_id)

        project_list = self.projects.find_one({"_id": bson.objectid.ObjectId(project_id)})["tasks"]
        if project_list:
            del project_list[int(task_id)]
            self.projects.update_one({"_id": bson.objectid.ObjectId(project_id)}, {"$set": {"tasks": project_list}})

    # Authentication

    def signup(self, email: str, name: str, password: str, user_type: str) -> bool:
        if self.users.find_one({"email": email}):  # If account already exists
            return True  # Account already exists

        self.users.insert_one({
            "email": email,
            "name": name,
            "password": bcrypt.hashpw(password.encode(), bcrypt.gensalt()),
            "type": user_type
        })

        return False  # Account doesn't already exist

    def login(self, email: str, password: str) -> str:
        user_doc = self.users.find_one({"email": email})

        if user_doc and bcrypt.checkpw(password.encode(), user_doc["password"]):
            token = random_string()
            self.users.update_one(user_doc, {"$push": {"tokens": token}})
            return str(user_doc["_id"]) + "*" + token
        else:
            return ""

    def user_by_token(self, raw_token) -> any:  # TODO: What type of object is this?
        if (raw_token is not None) and (len(raw_token.split("*")) == 2):
            user_id = raw_token.split("*")[0]

            try:
                garbage = bson.objectid.ObjectId(user_id)
            except bson.errors.InvalidId:  # Reject bad ObjectIds
                return None

            token = raw_token.split("*")[1]
            user_object = self.users.find_one({"_id": bson.objectid.ObjectId(user_id)})

            if token in user_object.get("tokens"):
                return user_object
        else:
            return None

    def is_authorized(self, token, target_id) -> bool:
        user_id, token, user_object = self.parse_token(token)

        if user_object and (token.split("*")[1] in user_object["tokens"]):
            target_object = self.projects.find_one({"_id": bson.objectid.ObjectId(target_id)})
            return target_object and (user_id in target_object["users"])

        return False

    # Getters

    def get_project(self, project_id: str) -> any:
        try:
            return self.projects.find_one({"_id", bson.objectid.ObjectId(project_id)})
        except bson.errors.InvalidId:
            return None

    def get_projects(self, user_doc: any) -> list:
        projects = []

        for project_id in user_doc.get("projects"):
            project = self.projects.find_one({"_id": project_id})
            if project:
                projects.append(project)

        return projects
