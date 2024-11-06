"""fetch details from courtreserve.com"""
from datetime import datetime, timedelta
import json
import logging
from urllib.request import urlopen, Request
from urllib.parse import urlencode


from models.time_slot import TimeSlot

logger = logging.getLogger(__name__)


def _read_expanded_api(org_id, start_date):
    url = "https://memberschedulers.courtreserve.com/SchedulerApi/ReadExpandedApi?id=10243&uiCulture=en-US&requestData=eb6Pn1vtmodO%2fy4NZJEchGdVYPE729Bz1Gt1aKWVGfZ0SdVw%2ffQrnxsxMxElybabX3%2b5Qv5xLqRtaI39RtH2lWSZ%2fnr1F444IsVX%2bSMAfN2cnZyUcS%2fr%2bQU27lG1cxSmgE4MdYyBk0Y%3d&sort=&group=&filter=&jsonData=%7B%22startDate%22%3A%222024-10-25T14%3A28%3A59.000Z%22%2C%22orgId%22%3A%2210243%22%2C%22TimeZone%22%3A%22America%2FNew_York%22%2C%22Date%22%3A%22Fri%2C%2025%20Oct%202024%2014%3A28%3A59%20GMT%22%2C%22KendoDate%22%3A%7B%22Year%22%3A2024%2C%22Month%22%3A10%2C%22Day%22%3A25%7D%2C%22UiCulture%22%3A%22en-US%22%2C%22CostTypeId%22%3A%22104773%22%2C%22CustomSchedulerId%22%3A%2215822%22%2C%22ReservationMinInterval%22%3A%2260%22%2C%22SelectedCourtIds%22%3A%2234737%2C34738%2C34739%2C34740%2C34788%2C34789%2C34790%22%2C%22SelectedInstructorIds%22%3A%22%22%2C%22MemberIds%22%3A%22%22%2C%22MemberFamilyId%22%3A%22%22%2C%22EmbedCodeId%22%3A%22%22%2C%22HideEmbedCodeReservationDetails%22%3A%22True%22%7D"

    headers = {"User-Agent": "Mozilla"}
    date = datetime.strptime(start_date, "%Y-%m-%d")
    json_data = {
        "startDate": f"{start_date}T04:00:00.000Z",
        "orgId": org_id,
        "TimeZone": "America/New_York",
        "Date": date.strftime("%a, %d %b %Y %H:%M:%S GMT"),
        "KendoDate": {
            "Year": date.year,
            "Month": date.month,
            "Day": date.day,
        },
        "UiCulture": "en-US",
        "CostTypeId": "104773",
        "CustomSchedulerId": "",
        "ReservationMinInterval": "60",
        "SelectedCourtIds": "",
        "SelectedInstructorIds": "",
        "MemberIds": "",
        "MemberFamilyId": "",
        "EmbedCodeId": "",
        "HideEmbedCodeReservationDetails": "True",
    }
    params_dict = {
        "id": org_id,
        "uiCulture": "en-US",
        "sort": "",
        "group": "",
        "filter": "",
        "jsonData": json.dumps(json_data),
    }
    params_qs = urlencode(params_dict)
    url = f"https://memberschedulers.courtreserve.com/SchedulerApi/ReadExpandedApi?{params_qs}"
    req = Request(url, headers=headers)
    logger.info("fetching %s", url)
    with urlopen(req) as r:
        return json.load(r)


def _filter_response(resp):
    """apply filter to response"""

    # only get items without a title
    data = list(filter(lambda d: d["Title"] == "", resp["Data"]))

    return {"Data": data}


def _find_blank_times(resp):
    pass


def _save_response(resp):
    logger.info("saving courtreserve_response.json ...")
    with open("courtreserve_response.json", "w") as f:
        f.write(json.dumps(resp, indent=2))


def _generate_time_slots(start_date):
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
    # Start time at 11:00 AM
    start_time = start_date.replace(hour=11, minute=0, second=0, microsecond=0)

    # End time at 5:00 AM the next day
    end_time = start_time + timedelta(days=1, hours=6)  # 5:00 AM the next day

    # List to store the datetime strings
    time_slots = []

    # Generate the time slots
    current_time = start_time
    while current_time <= end_time:
        time_slot = TimeSlot(datetime_str=current_time.strftime("%Y-%m-%dT%H:%M:%SZ"))
        time_slots.append(time_slot)
        current_time += timedelta(minutes=30)  # Increment by 30 minutes

    return time_slots


def _generate_time_slots_by_court(resp, start_date):
    all_court_labels = list(set([d["CourtLabel"] for d in resp["Data"]]))
    # print(all_court_labels)
    time_slots = _generate_time_slots(start_date)
    return {court_label: time_slots for court_label in all_court_labels}


def _get_times_from_booked_slots(booked_slots):
    pass


def _is_booked(slot, booked_slots):
    logger.info("slot: %s", slot)
    # print("slot:", slot)
    slot_dt_obj = datetime.strptime(slot.datetime_str, "%Y-%m-%dT%H:%M:%SZ")
    # print(booked_slots)
    for booked_slot in booked_slots:
        start = datetime.strptime(booked_slot["Start"], "%Y-%m-%dT%H:%M:%SZ")
        end = datetime.strptime(booked_slot["End"], "%Y-%m-%dT%H:%M:%SZ")
        if slot_dt_obj >= start and slot_dt_obj < end:
            return True

    return False


def _compare_resp_to_slots(resp, time_slots):
    for court_label, all_slots in time_slots.items():
        # print(court)
        booked_slots = [d for d in resp["Data"] if d["CourtLabel"] == court_label]
        for slot in time_slots[court_label]:
            slot.is_booked = _is_booked(slot, booked_slots)

    return time_slots


def fetch_courts(org_id, start_date):
    resp = _read_expanded_api(org_id, start_date)
    # resp = _filter_response(resp)
    time_slots = _generate_time_slots_by_court(resp, start_date)
    # print(time_slots_by_court)
    # print(time_slots)
    time_slots = _compare_resp_to_slots(resp, time_slots)
    print(time_slots)
    _save_response(resp)

    # return time_slots
    return {
        court_label: [s.asdict() for s in time_slots[court_label] if not s.is_booked]
        for court_label in time_slots
    }


def main():
    logging.basicConfig(level="DEBUG")
    org_id = 10243  # McCarren Park
    start_date = "2024-11-07"
    resp = fetch_courts(org_id, start_date)
    # print(resp)


if __name__ == "__main__":
    main()
