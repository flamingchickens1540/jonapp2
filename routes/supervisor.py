# Dynamic routes


class HybridRoute:
    def __init__(self, endpoint):
        self.endpoint = endpoint


def login(request, database):
    if request.method == "GET":
        return render_template("/supervisor/login.html")

    elif request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        verify, doc = database.login(email, password)
        if verify:
            session["id"] = str(doc["_id"])
            session["email"] = doc["email"]
            return redirect("/supervisor/home")
        else:
            return "Invalid username or password"




def signup():
    if request.method == "GET":
        return render_template("/supervisor/signup.html")

    elif request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if email and password:
            if database.signup(email, password):
                return redirect("/login")
            else:
                return "An account with this email already exists."
        else:
            return "You may not leave the username or password field blank."
