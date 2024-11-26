"""fetch details from aptussoft.com"""

from datetime import datetime
from http.cookiejar import CookieJar
import json
import logging
import re
from urllib.error import HTTPError
from urllib.request import urlopen, Request, build_opener, HTTPCookieProcessor
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


class APTUSSoft:
    """interact with the aptussoft API"""

    def __init__(self, subdomain, location, email, password):
        self._subdomain = subdomain
        self._location = location
        self._email = email
        self._password = password
        self._cookie_jar = CookieJar()
        self._opener = build_opener(HTTPCookieProcessor(self._cookie_jar))
        self._cookie = None
        self._verification_token = None
        self._cookie = self._fetch_cookie()
        self._verification_token = self._fetch_verification_token()

    def _fetch(self, path, payload):
        url = f"https://{self._subdomain}.aptussoft.com/{path}"
        headers = self._headers()
        logger.debug("headers %r", headers)
        data = urlencode(payload).encode()
        logger.info("request data: %s", data.decode())
        req = Request(url, headers=headers, data=data)
        logger.info("loading %s", url)
        try:
            with self._opener.open(req) as r:
                # with urlopen(req) as r:
                return json.load(r)
        except HTTPError as ex:
            logger.error("HTTPError %s from %s", ex.code, url)
            return None

    def _convert_to_iso8601(self, time_str, date_str):
        datetime_obj = datetime.strptime(date_str + " " + time_str, "%Y-%m-%d %H:%M")
        return datetime_obj.isoformat()

    def _get_verification_token(self, html):
        pattern = r"var TOKENHEADERVALUE = '(.*)';"
        return re.search(pattern, html).group(1)

    def _get_cookie(self):
        return f"{self._cookie or ''}; AccessEmail={self._email}; Accesspwd={self._password}"

    def _headers(self):
        headers = {
            # "cookie": self._cookie,
            "cookie": self._get_cookie(),
            # "origin": "https://prospectpark.aptussoft.com",
            # "Requestverificationtoken": self._verification_token or "",
            # "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "referer": "https://prospectpark.aptussoft.com/Member/Aptus/Calender",
        }
        if self._verification_token:
            headers["RequestVerificationToken"] = self._verification_token
        return headers

    def _fetch_cookie(self):
        url = f"https://{self._subdomain}.aptussoft.com/Member"
        # headers = self._headers()
        # print(headers)
        # req = Request(url, headers=self._headers())
        req = Request(url)
        with urlopen(req) as resp:
            # with self._opener.open(req) as resp:
            headers = resp.info()
            cookie = re.match(r"(.*?)\;", headers["Set-Cookie"]).group(1)
            # self._cookie = cookie
        logger.debug("cookie: %s", cookie)
        return cookie

    def _fetch_verification_token(self):
        headers = self._headers()
        url = f"https://{self._subdomain}.aptussoft.com/Member/Aptus/Calender"
        logger.debug("headers: %r", headers)
        req = Request(url, headers=headers)
        # req = Request(url)
        with urlopen(req) as resp:
            token = self._get_verification_token(resp.read().decode())
        logger.debug("token: %s", token)
        return token

    def _fetch_court_bookings(self, date):
        path = "Member/Aptus/CourtBooking_Get"
        payload = {
            # 'acctno': '14900',
            "locationid": "Brooklyn",
            "resourcetype": "Clay",
            "start": date,
            "end": date,
            "CalledFrom": "WEB",
        }
        logger.debug("payload %r", payload)
        return self._fetch(path, payload)

    def _fetch_operating_hours(self):
        path = "Member/Aptus/CourtBooking_ResourceListByLookupId"
        payload = {"locationid": self._location}
        return self._fetch(path, payload)

    def fetch_court_boooking(self):
        pass

    def _get_availability(self, operating_hours, date):
        court_open_time = operating_hours["ItemStime"]
        court_close_time = operating_hours["ItemEtime"]
        all_times = [
            f"{hour:02d}:{minute:02d}" for hour in range(24) for minute in [0, 30]
        ]
        # Find indices for open and close times
        try:
            index_open_time = all_times.index(court_open_time)
            index_close_time = all_times.index(court_close_time)
        except ValueError:
            return "Invalid operating hours received"

        # List of available times in the operating hours
        unformatted_available_times = all_times[index_open_time:index_close_time]

        # Convert times to ISO 8601 format
        available_times = [
            self._convert_to_iso8601(time, date) for time in unformatted_available_times
        ]
        return available_times

    def fetch_court_availability(self, date: str):
        """get all available times for a given date"""
        operating_hours = self._fetch_operating_hours()
        logger.debug("operating_hours %r", operating_hours)
        available_times = self._get_availability(operating_hours, date)
        # logger.debug("available_times %r", available_times)
        # Initialize booking counts
        booking_count = {time: 0 for time in available_times}
        formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%m/%d/%Y")
        bookings = self._fetch_court_bookings(formatted_date)

        logger.debug("bookings: %r", bookings)

        return {}


def main():
    """let's kick it off"""
    import os  # pylint: disable=import-outside-toplevel

    logging.basicConfig(level="DEBUG")
    try:
        email = os.environ["APTUS_EMAIL"]
        password = os.environ["APTUS_PASSWORD"]
    except KeyError:
        logger.error("need APTUS_EMAIL and APTUS_PASSWORD envvars set")
        return
    inst = APTUSSoft(
        subdomain="prospectpark", location="Brooklyn", email=email, password=password
    )

    date = "2024-11-20"
    resp = inst.fetch_court_availability(date)
    print(resp)


if __name__ == "__main__":
    main()
