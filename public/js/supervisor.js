// supervisor.js supervisor specific functions and frontend triggers for jonapp2
// Author: Nate Sales
//
// This file provides all supervisor specific functions and frontend triggers.
// It should be loaded after firebase and app.js. It depends on firebase and it's initialization.
// Additionally, the supervisor must already be authenticated.


// Wait for the DOM to load
document.addEventListener("DOMContentLoaded", () => {

    firebase.auth().onAuthStateChanged(_user => { // Update page if the authentication state changes
        if (_user) { // If logged in
            // Load all the elements on the supervisor page
            displayProjects(); // Display the projects
            displaySupervisorBanner(); // Show the login banner ("Logged in as...")
            initUserModal(); // Set up the user information modal.
        }
    });
});

/**
 * Display all a supervisor's projects on screen
 */
function displayProjects() {
    document.getElementById("table-body").innerHTML = ""; // Clear out the table
    let userDoc = db.collection("users").doc(user.uid); // Current supervisor's document

    userDoc.get().then(function (doc) { // Get the user doc
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
 * Trigger a modal popup.
 * @param user
 */
function displayProjectModal(user) {
    const name = document.getElementById("modal-name");
    name.value = user;
    $("#projectModal").modal(); // Show the modal
}

/**
 * Display supervisor banner
 */
function displaySupervisorBanner() {
    document.getElementById("banner").innerText = "Logged in as " + user.displayName;
}

/**
 * Delete a project and all it's users
 * @param id
 */
function deleteProject(id) {
    if (confirm('DANGER! Deleting this project will also remove it from all users and supervisors. Are you sure you want to delete this project?')) {
        console.log("Deleting project " + id + "...");
        // TODO

        // db.collection("projects").doc("DC").delete().then(function () {
        //     console.log("Document successfully deleted!");
        // }).catch(function (error) {
        //     console.error("Error removing document: ", error);
        // });
    }
}

/**
 * Create a new project
 * @param {string} name Name
 * @param {string} desc Description
 * @param {string} image base64 encoded image uri
 * @returns {string} document id
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
        });

        displayProjects(); // Update the projects list
        return docRef.id;
    });
}
