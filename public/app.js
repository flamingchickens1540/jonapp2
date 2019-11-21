var user;
const db = firebase.firestore();
const storage = firebase.storage();


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
  }).then(function(docRef) {
    console.log("Update complete.");
  }).catch(function(error) {
    console.error("Error updating supervisor: ", error);
  });
}

/** Register a new supervisor. */
function registerSupervisor(){
  updateSupervisor([]); // Update (create) the curent authenticated user.
}

/**
 * Assign given end user to supervisor.
 * @param {string} eid End user's ID.
 */
function assignEndUser(eid) {
  _supervisor().get().then(function(doc) {
    if (doc.exists) {
      endUsers = doc.data()["endusers"];
      endUsers.push(eid);
      updateSupervisor(endUsers)
    } else {
      console.log("Error: Supervisor doesn't exist.");
    }
  }).catch(function(error) {
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
  }).then(function(docRef) {
    console.log("Created end user.");
    assignEndUser(docRef.id);
  }).catch(function(error) {
    console.error("Error creating end user: ", error);
  });
}

/** Show available end users */
function showEndUsers() {
  _supervisor().get().then(function(doc) {
    endUsers = doc.data()["endusers"];

    for (i = 0; i < endUsers.length; i++) {
      document.getElementById("endusers").innerHTML = ""
      db.collection("endusers").doc(endUsers[i]).get().then(function(doc) {
        document.getElementById("endusers").innerHTML += "<li>" + doc.data()["name"] + "</li>";
      });
    }

  });
}

/** Trigger Google OAuth popup and assign user variable. */
function signIn() {
  const provider = new firebase.auth.GoogleAuthProvider();

  firebase.auth().signInWithPopup(provider).then(result => {
    user = result.user;

    _supervisor().get().then(function(doc) { // If the user is already a registered supervisor
      if(!doc.exists) {
        registerSupervisor()
      } else {
        console.log("Supervisor exists, no need to create it.")
      }
    }).catch(function(error) {
      console.error("Error getting supervisor's document:", error);
    });

    document.getElementById("banner").innerHTML = user.displayName + " logged in.";
  });
}
