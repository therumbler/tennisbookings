#!/usr/bin/env python3
from datetime import datetime
import logging

# from lib.courtreserve import fetch_courts
from lib.nycgovparks import fetch_available_courts
from lib.email import send_email

import settings

logger = logging.getLogger(__name__)


def fetch_all_available_courts():
    """fetch courts from all systems"""
    logging.basicConfig(level="INFO")
    # org_id = 10243  # McCarren Park
    # start_date = datetime.now().strftime("%Y-%m-%d")

    # court_reserve_resp = fetch_courts(org_id, start_date)
    court_id = 11
    nyc_gov_parks_resp = fetch_available_courts(court_id)
    return nyc_gov_parks_resp


def _timeslot_to_str(timeslot):
    """convert timeslot to string"""
    return f"{timeslot.court_name}|{timeslot.datetime_str}"


def _check_timeslot_if_notified(timeslot) -> bool:
    """check if the timeslot has been notified"""
    # check the notified.txt file for timeslot court_name and datetime_str
    # if found, return True
    # if not found, return False
    try:
        with open("notified.txt", "r") as f:
            lines = f.readlines()
            for line in lines:
                if _timeslot_to_str(timeslot) in line:
                    return True
    except FileNotFoundError:
        pass
    return False


def _should_notify(resp) -> bool:
    should_notify = False
    for timeslot in resp:
        if not _check_timeslot_if_notified(timeslot):
            should_notify = True

    return should_notify


def _notify(resp):
    body = "The following courts are available:\n"
    body += "\n".join([_timeslot_to_str(timeslot) for timeslot in resp])
    send_email(
        subject="NYC Parks Tennis Court Availability",
        body=body,
        to_email=settings.TO_EMAIL,
        from_email=settings.FROM_EMAIL,
        smtp_port=settings.SMTP_PORT,
        smtp_server=settings.SMTP_SERVER,
        username=settings.SMTP_USERNAME,
        password=settings.SMTP_PASSWORD,
    )


def main():
    """let's kick it all off"""
    resp = fetch_all_available_courts()
    if _should_notify(resp):
        logger.info("notifying")
        _notify(resp)
    print(resp)


if __name__ == "__main__":
    main()
