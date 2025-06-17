#!/usr/bin/env python3
import logging

from typing import List

from models.time_slot import TimeSlot
from lib.nycgovparks import fetch_available_courts
from lib.notify import send_email

import settings

logger = logging.getLogger(__name__)

NOTIFIED_TEXT_FILE_PATH = "notified.txt"


def fetch_all_available_courts():
    """fetch courts from all systems"""
    # org_id = 10243  # McCarren Park
    # start_date = datetime.now().strftime("%Y-%m-%d")

    # court_reserve_resp = fetch_courts(org_id, start_date)
    courts = []
    court_ids = [3, 11, 12]  # Riverside, McCarren Park, Central Park
    for court_id in court_ids:
        courts.extend(fetch_available_courts(court_id))

    return courts


def _timeslot_to_str(timeslot):
    """convert timeslot to string"""
    # turn datetime_obj into DDD, mmm, dd, HH:MM format
    datetime_str = timeslot.datetime_obj.strftime("%a, %b %d, %H:%M")

    return f"{timeslot.location_name}|{timeslot.court_name}|{datetime_str}"


def _check_timeslot_if_notified(timeslot) -> bool:
    """check if the timeslot has been notified"""
    timeslot_string = _timeslot_to_str(timeslot)
    try:
        with open(NOTIFIED_TEXT_FILE_PATH, "r") as f:
            lines = f.readlines()
            for line in lines:
                if timeslot_string in line:
                    return True
    except FileNotFoundError:
        logger.error("filenotfound")
        pass
    return False


def _mark_timeslot_as_notified(timeslot):
    """mark the timeslot as notified"""
    timeslot_string = _timeslot_to_str(timeslot)
    with open(NOTIFIED_TEXT_FILE_PATH, "a") as f:
        f.write(timeslot_string + "\n")
    logger.info("marked %s as notified", timeslot_string)


def _get_unnotified_timeslots(resp) -> List[TimeSlot]:
    timeslots = []
    for timeslot in resp:
        if not _check_timeslot_if_notified(timeslot):
            timeslots.append(timeslot)
    logger.info("%d new timeslots", len(timeslots))
    return timeslots


def _create_email_body(timeslots: List[TimeSlot]) -> str:
    """Create an email body from a list of timeslots."""
    body = "The following courts are available:\n"
    last_booking_url = ""
    for timeslot in timeslots:
        datetime_str = timeslot.datetime_obj.strftime("%a, %b %d, %H:%M")
        if timeslot.booking_url != last_booking_url:
            body += f"\n\n\n{timeslot.location_name}: {timeslot.booking_url}\n"
            last_booking_url = timeslot.booking_url
        body += f"{timeslot.court_name} | {datetime_str}\n"

    body += "\n"
    return body


def _notify(resp):
    body = _create_email_body(resp)
    logger.info("email body:\n%s", body)
    return send_email(
        subject="NYC Parks Tennis Court Availability",
        body=body,
        to_email=settings.TO_EMAIL,
        from_email=settings.FROM_EMAIL,
        smtp_port=settings.SMTP_PORT,
        smtp_server=settings.SMTP_SERVER,
        username=settings.SMTP_USERNAME,
        password=settings.SMTP_PASSWORD,
    )


def fetch_courts_and_notify():
    """let's kick it all off"""
    all_timeslots = fetch_all_available_courts()
    logger.info("found %d timeslots", len(all_timeslots))
    unnotified_timeslots = _get_unnotified_timeslots(all_timeslots)
    if not unnotified_timeslots:
        logger.info("no new timeslots available, not notifying")
        return
    logger.info("notifying")
    if _notify(unnotified_timeslots):
        logger.info("notification sent")
        for timeslot in unnotified_timeslots:
            _mark_timeslot_as_notified(timeslot)


if __name__ == "__main__":
    fetch_courts_and_notify()
