let user; // Authenticated user object
let db; // Firebase cloud firestore
let storage; // Firebase GCP Bucket

// Wait for the DOM to load. (Where the firebase libs are)
document.addEventListener("DOMContentLoaded", event => {
    db = firebase.firestore();
    storage = firebase.storage();

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
});

/**
 * Get currently authenticated supervisor's document
 * @returns {Object} Currently authenticated supervisor's doc
 */
function _supervisor() {
    return db.collection("supervisors").doc(user.uid);
}

/**
 * Register/update a new supervisor.
 * @param {array} endusers Array of end users.
 */
function updateSupervisor(endusers) {
    _supervisor().set({
        endusers: endusers
    }).then(function (docRef) { // Document ID
        console.log("Update complete.");
    }).catch(function (error) {
        console.error("Error updating supervisor: ", error);
    });
}

/** Register a new supervisor. */
function registerSupervisor() {
    updateSupervisor([]); // Update (create) the current authenticated user.
}

/**
 * Assign given end user to supervisor.
 * @param {string} eid End user's ID.
 */
function assignEndUser(eid) {
    _supervisor().get().then(function (doc) {
        if (doc.exists) {
            endUsers = doc.data()["endusers"];
            endUsers.push(eid);
            updateSupervisor(endUsers)
        } else {
            console.log("Error: Supervisor doesn't exist.");
        }
    }).catch(function (error) {
        console.error("Error getting supervisor's document:", error);
    });
}

/**
 * Create a new end user. (Does not assign to a supervisor)
 * @param {string} name The end user's name.
 * @returns {string} ID in endusers collection.
 */
function createEndUser(name) {
    db.collection("endusers").add({
        name: name,
        supervisors: [user.uid]
    }).then(function (docRef) {
        console.log("Created end user.");
        assignEndUser(docRef.id);
    }).catch(function (error) {
        console.error("Error creating end user: ", error);
    });
}
