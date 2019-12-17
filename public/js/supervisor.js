// supervisor.js supervisor specific functions and frontend triggers for jonapp2
// Author: Nate Sales
//
// This file provides all supervisor specific functions and frontend triggers.
// It should be loaded after firebase and app.js. It depends on firebase and it's initialization.
// Additionally, the supervisor must already be authenticated.


// Wait for the DOM to load
document.addEventListener("DOMContentLoaded", () => {
    firebase.auth().onAuthStateChanged(_user => {
        if (_user) {
            user = _user;
            pageInit();
        } else {
            console.log("!_user");
            logIn().then(() => { // Log in and display the banner.
                pageInit();
            });
        }
    });
});

/**
 * Initialize the page
 */
function pageInit() {
    displayProjects();
    displaySupervisorBanner();
    displayUserModal();
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

        db.collection("supervisors").doc(user.uid).update({
            projects: firebase.firestore.FieldValue.arrayUnion(docRef.id)
        });

        displayProjects(); // Update the projects list
        return docRef.id;
    });
}

/**
 * Generate project html <tr>
 * @param id
 * @param name
 * @param desc
 * @param image
 * @param user_len
 * @param task_len
 * @returns {string} Generated HTML
 */
function generateProjectHtml(id, name, desc, image, user_len, task_len) {
    return `<tr>
                <td class="align-middle" onclick="$('.collapse` + id + `').collapse('toggle')">
                    <div class="panel-group" id="accordion">
                        <div class="panel panel-default">
                            <div class="panel-heading">
                                <h5 class="panel-title mb-0">` + name + `</h5>
                            </div>
                            <div class="panel-collapse collapse in collapse` + id + `">
                                <div class="panel-body">
                                    <p>` + desc + `</p>
        
                                    <div class="container">
                                        <img alt="" class="img-fluid p-4" src="` + image + `">
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </td>
        
                <td class="align-middle" onclick="$('.collapse` + id + `').collapse('toggle')">` + user_len + `</td>
                <td class="align-middle" onclick="$('.collapse` + id + `').collapse('toggle')">` + task_len + `</td>
                <td class="align-middle">
                    <button class="btn btn-danger" onclick="displayProjectModal('` + id + `')" type="button">Edit</button>
                </td>
            </tr>`
}

function displayProjects() {

    document.getElementById("table-body").innerHTML = ""; // Clear out the table

    db.collection("supervisors").doc(user.uid).get().then(function (doc) {

        for (const project_id in doc.data()["projects"]) {
            const id = doc.data()["projects"][project_id];

            db.collection("projects").doc(id).get().then(function (doc) {
                document.getElementById("table-body").innerHTML += generateProjectHtml(id,
                    doc.data()["name"],
                    doc.data()["desc"],
                    doc.data()["image"],
                    doc.data()["users"].length,
                    doc.data()["tasks"].length);
            });

            console.log(document.getElementById("table-body").innerHTML)
        }
    });
}