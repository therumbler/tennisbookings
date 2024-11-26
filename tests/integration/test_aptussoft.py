import os
import unittest
import logging
from io import StringIO
from unittest.mock import patch
from lib.aptussoft import APTUSSoft


class TestAptusSoft(unittest.TestCase):
    def setUp(self) -> None:
        self.log_capture = StringIO()
        self.log_handler = logging.StreamHandler(self.log_capture)
        logging.basicConfig(level=logging.DEBUG, handlers=[self.log_handler])

        email = os.environ["APTUS_EMAIL"]
        password = os.environ["APTUS_PASSWORD"]

        self.aptus_instance = APTUSSoft(
            subdomain="prospectpark",
            location="Brooklyn",
            email=email,
            password=password,
        )
        return super().setUp()

    # @patch("logging.error")
    def test_fetch_court_bookings(self):
        date = "2024-11-20"
        resp = self.aptus_instance.fetch_court_availability(date)
        print(resp)

        log_contents = self.log_capture.getvalue()

        self.assertNotIn("ERROR", log_contents, "Error log was produced!")
