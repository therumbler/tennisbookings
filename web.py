import logging
from flask import Flask

from tennisbookings import fetch_all_available_courts_threads, fetch_calendar_string
from settings import LOG_LEVEL


def make_app():
    logging.basicConfig(level=LOG_LEVEL)
    app = Flask(__name__)

    @app.route("/")
    def index():
        return app.send_static_file("index.html")

    @app.route("/calendar.ics")
    def calendar():
        return (
            fetch_calendar_string(),
            200,
            {
                "Content-Type": "text/calendar",
                # "Content-Disposition": "attachment; filename=tennis.rumble.nyc.ics",
            },
        )

    @app.route("/api/timeslots")
    def timeslots():
        return fetch_all_available_courts_threads()

    @app.route("/<path:path>")
    def static_files(path):
        return app.send_static_file(path)

    return app
