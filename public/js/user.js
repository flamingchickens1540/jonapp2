/**
 * Trigger login popup and redirect
 */
function logIn() {
    firebase.auth().onAuthStateChanged(user => {
        if (!user) {
            const provider = new firebase.auth.GoogleAuthProvider();

            firebase.auth().signInWithPopup(provider).then(() => {
                let supervisor = db.collection("supervisors").doc(user.uid);

                if (!exists(supervisor)) { // If supervisor doesn't exist
                    supervisor.set({
                        users: [] // Initialize empty users array
                    });
                }
                window.location = "/supervisor/home.html";
            });
        } else {
            window.location = "/supervisor/home.html";
        }
    });
}

/**
 * Log out current user
 */
function logOut() {
    firebase.auth().signOut();
    window.location = "/";
}

function displaySupervisorBanner() {
    firebase.auth().onAuthStateChanged(user => {
        if (user) {
            document.getElementById("banner").innerText = "Logged in as " + user.displayName;
        }
    });
}