#!/usr/bin/env python3
import logging

from typing import List

# from lib.courtreserve import fetch_courts
from models.time_slot import TimeSlot
from lib.nycgovparks import fetch_available_courts
from lib.notify import send_email

import settings

logger = logging.getLogger(__name__)

NOTIFIED_TEXT_FILE_PATH = "notified.txt"


def fetch_all_available_courts():
    """fetch courts from all systems"""
    logging.basicConfig(level="INFO")
    # org_id = 10243  # McCarren Park
    # start_date = datetime.now().strftime("%Y-%m-%d")

    # court_reserve_resp = fetch_courts(org_id, start_date)
    courts = []
    court_ids = [11, 12]  # McCarren Park, Central Park
    for court_id in court_ids:
        courts.extend(fetch_available_courts(court_id))

    return courts


def _timeslot_to_str(timeslot):
    """convert timeslot to string"""
    return f"{timeslot.location_name}|{timeslot.court_name}|{timeslot.datetime_str}"


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
    with open(NOTIFIED_TEXT_FILE_PATH, "a") as f:
        f.write(_timeslot_to_str(timeslot) + "\n")
    logger.info(f"marked {timeslot.court_name} at {timeslot.datetime_str} as notified")


def _get_unnotified_timeslots(resp) -> List[TimeSlot]:
    timeslots = []
    for timeslot in resp:
        if not _check_timeslot_if_notified(timeslot):
            timeslots.append(timeslot)
    logger.info("%d new timeslots", len(timeslots))
    return timeslots


def _notify(resp):
    body = "The following courts are available:\n"
    body += "\n".join([_timeslot_to_str(timeslot) for timeslot in resp])
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


def main():
    """let's kick it all off"""
    logging.basicConfig(level="INFO")
    resp = fetch_all_available_courts()
    logger.info("found %d timeslots", len(resp))
    unnotified_timeslots = _get_unnotified_timeslots(resp)
    if not unnotified_timeslots:
        logger.info("no new timeslots available, not notifying")
        return
    logger.info("notifying")
    if _notify(unnotified_timeslots):
        logger.info("notification sent")
        for timeslot in unnotified_timeslots:
            _mark_timeslot_as_notified(timeslot)


if __name__ == "__main__":
    main()
