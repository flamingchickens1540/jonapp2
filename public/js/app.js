let user; // Currently authenticated user (supervisor)
let db; // Firebase cloud firestore
let storage; // Firebase GCP Bucket

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

    firebase.auth().onAuthStateChanged(_user => {
        user = _user;
    });
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
 * Log in if not already and redirect.
 * @param url
 */
function cleanLogin(url) {
    if (user) {
        window.location = url;
    } else {
        logIn().then(() => {
            window.location = url;
        });
    }
}

/**
 * Trigger login popup and redirect
 * @return {Promise} login popup completion
 */
function logIn() {
    const provider = new firebase.auth.GoogleAuthProvider();

    return firebase.auth().signInWithPopup(provider).then(result => {
        user = result.user;

        let supervisor = db.collection("supervisors").doc(user.uid);

        if (!exists(supervisor)) { // If supervisor doesn't exist
            supervisor.set({
                users: [] // Initialize empty users array
            });
        }
    });
}

/**
 * Log out current user
 */
function logOut() {
    firebase.auth().signOut().then(() => {
        window.location = "/";
    });
}

/**
 * Delete account
 * DANGER! This is irreversible and may cause orphan documents (Projects or users)
 */
function deleteAccount() {
    if (confirm('DANGER! This can leave users without a supervisor. Make sure to transfer your users to another supervisor before deleting your account. Are you sure you want to delete your account?')) {
        logOut();
        window.location = '/';
    }
}

function displayUserModal() {
    new QRCode(document.getElementById("qr"), {
        text: user.uid,
        correctLevel: QRCode.CorrectLevel.H
    });
    document.getElementById("qr-text").value = user.uid;
    document.getElementById("user-email").innerText = user.email;
}

function copyUserCode() {
    const copyText = document.getElementById("qr-text");
    copyText.select();
    copyText.setSelectionRange(0, 99999);
    document.execCommand("copy");
}

//
// /**
//  * Create a new end user and assign current supervisor to it.
//  * @param {string} name The end user's name.
//  * @returns {Promise} db operation
//  */
// function createUser(name) {
//     return db.collection("users").add({ // Create the user
//         name: name,
//         supervisors: [user.uid], // With the current supervisor pre-authorized.
//         projects: []
//     }).then(function (docRef) {
//         db.collection("supervisors").doc(user.uid).update({
//             users: firebase.firestore.FieldValue.arrayUnion(docRef.id)
//         });
//     });
// }
//
//
// /**
//  * Authorize a supervisor for a user.
//  * @param {string} supervisor Supervisor's ID
//  * @param {string} user User's ID
//  * @returns {Promise} db operation
//  */
// function addSupervisor(supervisor, user) {
//     return db.collection("users").doc(user).update({
//         supervisors: firebase.firestore.FieldValue.arrayUnion(supervisor)
//     });
// }
//
//
// /**
//  * Remove a supervisor from a user.
//  * @param {string} supervisor Supervisor's ID
//  * @param {string} user User's ID
//  * @returns {Promise} db operation
//  */
// function removeSupervisor(supervisor, user) {
//     return db.collection("users").doc(user).update({
//         supervisors: firebase.firestore.FieldValue.arrayRemove(supervisor)
//     });
// }
//
//
// /**
//  * Get array of users
//  * @returns {array} Users //TODO
//  */
// function getUsers() {
//     firebase.auth().onAuthStateChanged(user => {
//         db.collection("supervisors").doc(user.uid).get().then(function (doc) {
//             users = doc.data()["users"];
//
//             for (i = 0; i < users.length; i++) {
//                 db.collection("users").doc(users[i]).get().then(function (doc) {
//                     console.log(doc.data());
//                 });
//             }
//         });
//     });
// }
//
//
// /**
//  * Create a new project
//  * @param {string} name Name
//  * @param {string} desc Description
//  * @param {string} image_url URL of image
//  * @returns {Promise} db operation
//  */
// function createProject(name, desc, image_url) {
//     return db.collection("projects").add({ // Create the project
//         name: name,
//         desc: desc,
//         image_url: image_url,
//         authorized_users: [user.uid], // Pre-authorize current supervisor for use in this project.
//         tasks: []
//     }).then(function (docRef) {
//         console.log("Created project " + docRef.id);
//     });
// }
