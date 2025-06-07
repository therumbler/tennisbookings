"""fetch tennis info from nycgovparks.gov"""

from datetime import datetime, timedelta
import re
import logging
from urllib.request import urlopen, Request
from urllib.parse import urlencode


from models.time_slot import TimeSlot

logger = logging.getLogger(__name__)


def _fetch_html(court_id):
    url = f"https://www.nycgovparks.org/tennisreservation/availability/{court_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "accept": "text/html",
    }
    req = Request(url, headers=headers)
    logger.info("fetching %s", url)
    with urlopen(req) as resp:
        return resp.read().decode()


def _get_rows_from_div(div):
    rows_pattern = r"<tr>.*?</tr>"
    rows = re.findall(rows_pattern, div)
    return rows


def _get_time_from_row(row):
    time_string = _get_time_string_from_row(row)


def _get_time_string_from_row(row):
    time_pattern = r"<strong>(.*?)</strong>"
    time = None
    try:
        time = re.search(time_pattern, row).group(1)
    except AttributeError:
        logger.warning("row %s does not have a time", row)

    return time


def _time_string_to_datetime(time_string, date):
    # create a datetime object from date (yyyy-mm-dd) and time (h:mm p.m/a.m) variables
    dt_str = None
    try:
        dt_str = f"{date} {time_string.replace('.', '').upper()}"
        dt = datetime.strptime(dt_str, "%Y-%m-%d %I:%M %p")
    except Exception as e:
        logger.warning(
            "Could not parse datetime from date '%s' and time '%s': %s",
            date,
            time_string,
            e,
        )
    return dt


def _get_timeslot_from_row(row, date, court_name, location_name):
    # logger.debug("row %s", row)
    time_string = _get_time_string_from_row(row)
    dt = _time_string_to_datetime(time_string, date)

    # logger.info("dt: %s", dt)
    if "status2" in row:
        is_booked = False
    else:
        is_booked = True

    return TimeSlot(
        datetime_str=str(dt),
        datetime_obj=dt,
        is_booked=is_booked,
        court_name=court_name,
        location_name=location_name,
    )


def _div_to_timeslots(location_name, div):
    date = re.search(r"\d{4}-\d{2}-\d{2}", div).group()
    rows = _get_rows_from_div(div)
    time_slots = []
    court_name = ""
    for row in rows:
        if "Court" in row:
            court_name = re.search(r"Court \d", row).group()
        else:
            time_slots.append(
                _get_timeslot_from_row(row, date, court_name, location_name)
            )
    time_slots = [ts for ts in time_slots if ts]
    logger.debug("found %d timeslots on %s", len(time_slots), date)
    return time_slots


def _get_timeslots_from_html(html):
    location_name = re.search(r"<h3>(.*?)</h3>", html).group(1)

    pattern = r'<div id="\d{4}-\d{2}-\d{2}".*?</div>'
    matches = re.findall(pattern, html, re.DOTALL)

    if not matches:
        logger.error("no matches found in html")
    timeslots: list[TimeSlot] = []
    for div in matches:
        timeslots.extend(_div_to_timeslots(location_name, div))

    return timeslots


def _fetch_all_courts(court_id):
    html = _fetch_html(court_id)

    return _get_timeslots_from_html(html)


def fetch_available_courts(court_id):
    resp = _fetch_all_courts(court_id)

    return [ts for ts in resp if not ts.is_booked]


def main():
    logging.basicConfig(level="DEBUG")
    court_id = 11  # McCarren Park

    resp = fetch_available_courts(court_id)
    # print(resp)


if __name__ == "__main__":
    main()
