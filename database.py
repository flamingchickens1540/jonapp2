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

    # Image methods

    def get_image(self, object_id: str):
        """
        Get an image from GridFS and convert to base64 string
        :param object_id: Image ID
        :return: base64 string
        """
        try:
            entry = self.gridfs.get(object_id)
        except gridfs.errors.NoFile:
            return None

        if entry.contentType.strip().split("/")[0] != "image":  # If not an image, delete it.
            self.gridfs.delete(object_id)
            return None

        return "data:" + entry.contentType + ";base64, " + base64.b64encode(entry.read()).decode()

    def put_image(self, image):
        """
        Upload an image to GridFS
        :param image: Image
        :return: Error as string
        """
        if image and image.filename:
            try:
                extension = image.filename.split(".")[1]
            except IndexError:  # No extension
                return "No image extension specified"
            else:
                if image.content_type.split("/")[0] == "image":
                    self.gridfs.put(image, content_type=image.content_type, filename="image-" + random_string() + "." + extension)
        else:
            return "No image specified"

    def delete_image(self, string_id):
        """
        Delete a GridFS image
        :param string_id: Image ID
        :return:
        """
        return self.gridfs.delete(bson.objectid.ObjectId(string_id))

    # Projects

    def create_project(self, name: str, description: str, image, user: str):
        """
        Create a new project
        :param name: Project name
        :param description: Project description
        :param image: Project image
        :param user: First user to authorize to access this project
        """
        # TODO: Type checking and error handling

        new_project = self.projects.insert_one({
            "name": name,
            "description": description,
            "image": image,  # TODO: replace with self.put_image(image),
            "users": [user]
        })

        self.users.update_one({"_id": user}, {"$push": {"projects": str(new_project.inserted_id)}})

    def update_project(self, project_id: str, name: str, description: str, image):
        """
        Update a project
        :param project_id: Project's ID
        :param name: New project name
        :param description: New project description
        :param image: New project image
        """
        self.projects.update_one({'_id': bson.objectid.ObjectId(project_id)}, {'$set': {
            "name": name,
            "description": description,
            "image": self.put_image(image),
        }})

    def delete_project(self, project_id: str):
        """
        Delete a project
        :param project_id: Project to delete
        """
        project_doc = self.projects.find_one({"_id": bson.objectid.ObjectId(project_id)})
        if not project_doc:  # If project with project_id doesn't exist, no need to do anything.
            return
        else:  # If it does exit, delete it.
            project_image = project_doc["image"]
            if project_image:
                self.delete_image(project_image)

            self.projects.delete_one({"_id": bson.objectid.ObjectId(project_id)})

    # Tasks

    def create_task(self, project_id: str, name: str, description: str, image):
        """
        Create a task
        :param project_id: Project ID to create task under
        :param name: Task's name
        :param description: Task's description
        :param image: Task's image
        :return: Error as string
        """
        if not self.projects.find_one({"_id": bson.objectid.ObjectId(project_id)}):
            return "Project not found"

        self.projects.update_one({"_id": bson.objectid.ObjectId(project_id)}, {"$push": {"tasks": {
            "name": name,
            "description": description,
            "image": self.put_image(image),
            "state": "Pending",
            "subtasks": []
        }}})

    def update_task(self, project_id: str, task: str, name: str, description: str, image) -> str:
        """
        Update a task
        :param project_id: ID of project
        :param task: Task integer
        :param name: New task name
        :param description: New task description
        :param image: New task image
        :return: Error as string
        """
        if not self.projects.find_one({"_id": bson.objectid.ObjectId(project_id)}):
            return "Project not found"

        if image == 'none':
            self.projects.update_one({"_id": bson.objectid.ObjectId(project_id)}, {"$set": {"tasks." + task: {  # Append the new task
                "name": name,
                "description": description,
            }}})
        else:
            self.projects.update_one({"_id": bson.objectid.ObjectId(project_id)}, {"$set": {"tasks." + task: {
                "name": name,
                "description": description,
                "image": self.put_image(image),
            }}})

    def delete_task(self, project_id, task_id):
        """
        Delete a task
        :param project_id: Project that task belongs to
        :param task_id: Task integer
        """
        print("Deleting index " + str(task_id) + " from " + project_id)

        project_list = self.projects.find_one({"_id": bson.objectid.ObjectId(project_id)})["tasks"]
        if project_list:
            del project_list[int(task_id)]
            self.projects.update_one({"_id": bson.objectid.ObjectId(project_id)}, {"$set": {"tasks": project_list}})

    # Authentication

    def signup(self, email: str, name: str, password: str, user_type: str) -> bool:
        """
        Register a new user
        :param email: User's email
        :param name: User's name
        :param password: User's plaintext password
        :param user_type: Type of user (user || supervisor)
        :return: True if user's email already exists in database, False otherwise
        """
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
        """
        Generate an authentication token
        :param email: User's email
        :param password: User's password
        :return: Authentication token
        """
        user_doc = self.users.find_one({"email": email})

        if user_doc and bcrypt.checkpw(password.encode(), user_doc["password"]):
            token = random_string()
            self.users.update_one(user_doc, {"$push": {"tokens": token}})
            return str(user_doc["_id"]) + "*" + token
        else:
            return ""

    def user_by_token(self, raw_token) -> any:  # TODO: What type of object is this?
        """
        Parse a raw token cookie and return user object
        :param raw_token: Authentication token
        :return: User document
        """
        if (raw_token is not None) and (len(raw_token.split("*")) == 2):
            user_id = raw_token.split("*")[0]
            token = raw_token.split("*")[1]
            
            try:
                user_object = self.users.find_one({"_id": bson.objectid.ObjectId(user_id)})
            except bson.errors.InvalidId:  # Reject bad ObjectIds
                return None

            if token in user_object.get("tokens"):
                return user_object
        else:
            return None

    # # Deprecate this
    # def is_authorized(self, token, target_id) -> bool:
    #     user_id, token, user_object = self.parse_token(token)
    #
    #     if user_object and (token.split("*")[1] in user_object["tokens"]):
    #         target_object = self.projects.find_one({"_id": bson.objectid.ObjectId(target_id)})
    #         return target_object and (user_id in target_object["users"])
    #
    #     return False

    # Getters

    def get_project(self, project_id: str) -> any:
        """
        Get a single project
        :param project_id: ID of project document
        :return: Project document
        """
        try:
            return self.projects.find_one({"_id", bson.objectid.ObjectId(project_id)})
        except bson.errors.InvalidId:
            return None

    def get_projects(self, user_doc: any) -> list:
        """
        Get all projects for a user
        :param user_doc: User document
        :return: List of projects
        """
        projects = []

        projects_available = user_doc.get("projects")
        if projects_available:
            for project_id in projects_available:
                project = self.get_project(project_id)
                if project:
                    projects.append(project)

        return projects
