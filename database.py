# database.py Database wrappers for jonapp2
# Author: Nate Sales
#
# This file provides safe wrappers for database operations.
# It may be imported anywhere in the main server file.

import base64

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
        self._projects = self._db["projects"]
        self._tasks = self._db["tasks"]
        self._users = self._db["users"]

    def get_image(self, object_id):  # TODO: No content_type checking. This should only allow images
        entry = self._gridfs.get(object_id)
        content_type = entry.contentType.strip()

        if content_type.split("/")[0] != "image":
            raise ValueError("Content type " + content_type + " not supported.")

        content = entry.read()
        return "data:" + content_type + ";base64, " + base64.b64encode(content).decode()

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
            "projects": []
        }).inserted_id)

    def add_project(self, name, description):
        return str(self._projects.insert_one({
            "name": name,
            "description": description,
            "tasks": []
        }).inserted_id)

    def add_task(self, project, name, description, image):
        task_id = str(self._tasks.insert_one({
            "project": project,
            "name": name,
            "description": description,
            "image": self._gridfs.put(image, content_type=image.content_type, filename=image.filename)
        }).inserted_id)

        if not task_id:
            raise ValueError("Project id: " + project + " not found.")

        self._projects.update_one({"_id": ObjectId(project)}, {"$push": {"tasks": task_id}})
        return task_id

    def get_tasks_html(self, project):
        tasks_html = ""

        tasks = self._projects.find_one({"_id": ObjectId(project)})["tasks"]
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

# def delete_task(self, string_id):
#     image_id = self._users.find_one({'_id': ObjectId(string_id)})["tasks"]
# # return self._gridfs.delete(ObjectId(string_id))
