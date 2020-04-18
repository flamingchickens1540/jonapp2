from flask import Flask, request, render_template


def staticFormRoute(formProcessor, arguments, argumentError="Please fill out all required fields."):
    endpoint = str(request.url_rule)[1:]
    if endpoint == "/":
        endpoint = "index.html"

    if request.method == "GET":
        return render_template(endpoint + ".html")
    elif request.method == "POST":
        processor_arguments = []

        for arg in arguments:
            if arg not in request.form:
                return argumentError
            else:
                processor_arguments.append(request.form[arg])

        return formProcessor(*processor_arguments)


def supervisor_login(username, password):
    if username == "nate@nate.to" and password == "test":
        return "welcome"
    else:
        return "not welcome"


app = Flask(__name__)


@app.route("/supervisor/login", methods=["GET", "POST"])
def route_index():
    return staticFormRoute(supervisor_login, ["email", "password"])


app.run("localhost", port=5000)
