// supervisor.js supervisor specific functions and frontend triggers for jonapp2
// Authors: Nate Sales and Seth Knights
//
// This file provides all supervisor specific functions and frontend triggers.
// It should be loaded after firebase and app.js. It depends on firebase and it's initialization.
// Additionally, the supervisor must already be authenticated.


// Wait for the DOM to load
document.addEventListener("DOMContentLoaded", () => {

    // firebase.auth().onAuthStateChanged(_user => { // Update page if the authentication state changes
    //     if (user) { // If logged in
    //         // Load all the elements on the supervisor page
    //         displayProjects(); // Display the projects
    //         displaySupervisorBanner(); // Show the login banner ("Logged in as...")
    //         initUserModal(); // Set up the user information modal.
    //     }
    // });
});

/**
 * Display all a supervisor's projects on screen
 */
function displayProjects() {
    document.getElementById("table-body").innerHTML = ""; // Clear out the table
    let userDoc = db.collection("users").doc(user.uid); // Current supervisor's document

    userDoc.get().then(function (doc) { // Get the user doc
        if (doc.data()) { // If there is a doc
            const projects = doc.data()["projects"]; // The projects that the supervisor has access to

            if (projects != null) { // If there are any projects
                console.log("Iterating over projects...");

                for (let i = 0; i < projects.length; i++) {
                    const projectId = projects[i]; // Current project

                    db.collection("projects").doc(projectId).get().then(function (doc) {
                        project = doc.data();

                        document.getElementById("table-body").innerHTML += `
                <tr>
                    <td class="align-middle" onclick="$('.collapse` + projectId + `').collapse('toggle')">
                        <div class="panel-group" id="accordion">
                            <div class="panel panel-default">
                                <div class="panel-heading">
                                    <h5 class="panel-title mb-0">` + project["name"] + `</h5>
                                </div>
                                <div class="panel-collapse collapse in collapse` + projectId + `">
                                    <div class="panel-body">
                                        <p>` + project["desc"] + `</p>
            
                                        <div class="container">
                                            <img alt="" class="img-fluid p-4" src="` + project["image"] + `">
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </td>
            
                    <td class="align-middle" onclick="$('.collapse` + projectId + `').collapse('toggle')">` + project["users"].length + `</td>
                    <td class="align-middle" onclick="$('.collapse` + projectId + `').collapse('toggle')">` + project["tasks"].length + `</td>
                    <td class="align-middle">
                        <button class="btn btn-danger" onclick="displayProjectModal('` + projectId + `')" type="button">Edit</button>
                    </td>
                </tr>`
                    });
                }
            } else {
                console.log("No projects detected.");
            }
        } else {
            console.log("Doc !data()");
            logIn().then(() => location.reload());
        }
    });
}

function initUserModal() {
    new QRCode(document.getElementById("qr"), {
        text: user.uid,
        correctLevel: QRCode.CorrectLevel.H
    });
    document.getElementById("qr-text").value = user.uid;
    document.getElementById("user-email").innerText = user.email;
}

/**
 * Trigger project edit modal popup
 * @param id ID of project in question
 */
function displayProjectModal(id) {
    db.collection("projects").doc(id).get().then(function (doc) {
        project = doc.data();

        let name = document.getElementById("p-edit-name");
        let desc = document.getElementById("p-edit-desc");
        let image = document.getElementById("p-edit-image");
        let pid = document.getElementById("p-edit-id");

        name.value = project["name"];
        desc.value = project["desc"];
        image.src = project["image"];
        pid.value = id;

    }).then(() => {
        $("#projectEditModal").modal(); // Show the modal
    });
}

/**
 * Display supervisor banner
 */

function displaySupervisorBanner() {
    document.getElementById("banner").innerText = "Logged in as " + user.displayName;
}

/**
 * Delete a project and entry of all it's users
 * @param id ID of project to delete
 */
function deleteProject(id) {
    // if (confirm('DANGER! Deleting this project will also remove it from all users and supervisors. Are you sure you want to delete this project?')) {
    //     console.log("Deleting project " + id + "...");
    // }
    db.collection("projects").doc(id).get().then(function (doc) {
        const users = doc.data()["users"];

        if (users != null) { // If there are any users
            for (let i = 0; i < users.length; i++) {
                const userId = users[i]; // Current project

                db.collection("users").doc(userId).update({
                    projects: firebase.firestore.FieldValue.arrayRemove(id)
                });
            }
        }
    }).then(() => {
        db.collection("projects").doc(id).delete().then(() => {
            alert("Project deleted.");
            displayProjects();
        });
    });
}

/**
 * Create a new project
 * @param {string} name Name
 * @param {string} desc Description
 * @param {string} image base64 encoded image uri
 */
function createProject(name, desc, image) {
    db.collection("projects").add({ // Create the project
        name: name,
        desc: desc,
        image: image,
        users: [user.uid], // Pre-authorize current supervisor for use in this project.
        tasks: []
    }).then(function (docRef) {
        alert("Project \"" + name + "\" created.");

        db.collection("users").doc(user.uid).update({
            projects: firebase.firestore.FieldValue.arrayUnion(docRef.id)
        }).then(() => {
            displayProjects(); // Update the projects list
        });
    });
}

/**
 * Edit an existing project from modal
 */
function updateProject() {
    let name = document.getElementById("p-edit-name").value;
    let desc = document.getElementById("p-edit-desc").value;
    let image = document.getElementById("p-edit-image").src;
    let id = document.getElementById("p-edit-id").value;

    console.log("Going to update " + id);

    db.collection("projects").doc(id).update({ // Create the project
        name: name,
        desc: desc,
        image: image,
        // users: [user.uid], // Pre-authorize current supervisor for use in this project.
        // tasks: []
    }).then(function () {
        alert("Project \"" + name + "\" updated.");
        displayProjects();
    });
}

function addProjectUser(uid) { // Add user to project from QR code/user code. TODO: Write JS and DB rules to allow users to add projects to other users.

    let pid = document.getElementById("p-edit-id");

    console.log("Project ID " + pid.value);
    console.log("User ID " + uid);

    db.collection("projects").doc(pid.value).update({
        users: firebase.firestore.FieldValue.arrayUnion(uid)
    }).then(function () {
        console.log('Project ' + pid.value + ' updated successfully');
    }).catch(function (error) {
        console.error("Error updating document: ", error);
    });

    //db.collection("users").doc(uid).update({
    //    projects: firebase.firestore.FieldValue.arrayUnion(pid.value)
    //}).then(function () {
    //    console.log('Project ' + pid.value + ' added to user: ' + uid);
    //}).catch(function (error) {
    //    console.error("Error adding user to project: ", error);
    //})
}