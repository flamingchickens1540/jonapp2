// Wait for the DOM to load. (Where the firebase libs are)
document.addEventListener("DOMContentLoaded", () => {
    firebase.auth().onAuthStateChanged(_user => {
        if (_user) {
            user = _user;
            pageInit();
        } else {
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
    displaySupervisorBanner();
    renderUserModal();
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

function deleteProject() {
    confirm('Are you sure you want to delete this project?');
}