import logging
from flask import Flask

from tennisbookings import fetch_all_available_courts
from settings import LOG_LEVEL


def make_app():
    logging.basicConfig(level=LOG_LEVEL)
    app = Flask(__name__)

    @app.route("/")
    def index():
        return app.send_static_file("index.html")

    @app.route("/api/timeslots")
    def timeslots():
        return fetch_all_available_courts()

    return app
