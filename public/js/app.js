let db; // Firebase cloud firestore
let storage; // Firebase GCP Bucket

// Wait for the DOM to load. (Where the firebase libs are)
document.addEventListener("DOMContentLoaded", () => {
    db = firebase.firestore();
    storage = firebase.storage();

    if (!firebase.apps.length) {
        firebase.initializeApp({ // This is all client-side safe.
            apiKey: "AIzaSyDLGdqO7cCBoMWRvUD2Iy8gMVZ-bYUBGbE",
            authDomain: "jonapp-2.firebaseapp.com",
            databaseURL: "https://jonapp-2.firebaseio.com",
            projectId: "jonapp-2",
            storageBucket: "jonapp-2.appspot.com",
            messagingSenderId: "851985231577",
            appId: "1:851985231577:web:67563f2397c4d08dea18c8",
            measurementId: "G-77EKECDTF7"
        });
    }
});


/**
 * Check if a document exists
 * @param docRef Firestore document. For example db.collection("supervisors").doc(user.uid)
 * @return {boolean} Does the doc exist?
 */
function exists(docRef) {
    docRef.get().then(function (doc) {
        return doc.exists;
    });
}


/**
 * Create a new end user and assign current supervisor to it.
 * @param {string} name The end user's name.
 * @returns {Promise} db operation
 */
function createUser(name) {
    return db.collection("users").add({ // Create the user
        name: name,
        supervisors: [user.uid], // With the current supervisor pre-authorized.
        projects: []
    }).then(function (docRef) {
        db.collection("supervisors").doc(user.uid).update({
            users: firebase.firestore.FieldValue.arrayUnion(docRef.id)
        });
    });
}


/**
 * Authorize a supervisor for a user.
 * @param {string} supervisor Supervisor's ID
 * @param {string} user User's ID
 * @returns {Promise} db operation
 */
function addSupervisor(supervisor, user) {
    return db.collection("users").doc(user).update({
        supervisors: firebase.firestore.FieldValue.arrayUnion(supervisor)
    });
}


/**
 * Remove a supervisor from a user.
 * @param {string} supervisor Supervisor's ID
 * @param {string} user User's ID
 * @returns {Promise} db operation
 */
function removeSupervisor(supervisor, user) {
    return db.collection("users").doc(user).update({
        supervisors: firebase.firestore.FieldValue.arrayRemove(supervisor)
    });
}


/**
 * Get array of users
 * @returns {array} Users //TODO
 */
function getUsers() {
    firebase.auth().onAuthStateChanged(user => {
        db.collection("supervisors").doc(user.uid).get().then(function (doc) {
            users = doc.data()["users"];

            for (i = 0; i < users.length; i++) {
                db.collection("users").doc(users[i]).get().then(function (doc) {
                    console.log(doc.data());
                });
            }
        });
    });
}


/**
 * Create a new project
 * @param {string} name Name
 * @param {string} desc Description
 * @param {string} image_url URL of image
 * @returns {Promise} db operation
 */
function createProject(name, desc, image_url) {
    return db.collection("projects").add({ // Create the project
        name: name,
        desc: desc,
        image_url: image_url,
        authorized_users: [user.uid], // Pre-authorize current supervisor for use in this project.
        tasks: []
    }).then(function (docRef) {
        console.log("Created project " + docRef.id);
    });
}
