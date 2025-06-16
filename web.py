from flask import Flask

from tennisbookings import fetch_all_available_courts


def make_app():
    app = Flask(__name__)

    @app.route("/")
    def index():
        return app.send_static_file("index.html")

    @app.route("/api/timeslots")
    def timeslots():
        return fetch_all_available_courts()

    return app
