/** Show available end users */
function showEndUsers() {
    let supervisor = _supervisor();

    if (typeof supervisor == "undefined") {
        alert("Please log in");
        return;
    }

    supervisor.get().then(function (doc) {
        endUsers = doc.data()["endusers"];

        for (i = 0; i < endUsers.length; i++) {
            document.getElementById("endusers").innerHTML = "";
            db.collection("endusers").doc(endUsers[i]).get().then(function (doc) {
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

        let supervisor = _supervisor();

        if (typeof supervisor == "undefined") {
            alert("Error: _supervisor() undefined. This should never happen.");
            return;
        }

        supervisor.get().then(function (doc) { // If the user is already a registered supervisor
            if (!doc.exists) {
                registerSupervisor()
            } else {
                console.log("Supervisor exists, no need to create it.")
            }
        }).catch(function (error) {
            console.error("Error getting supervisor's document:", error);
        });

        document.getElementById("banner").innerHTML = user.displayName + " logged in.";
    });
}
