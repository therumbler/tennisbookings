"""fetch details from courtreserve.com"""
from datetime import datetime
import json
import logging
from urllib.request import urlopen, Request
from urllib.parse import urlencode

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


def fetch_courts(org_id, start_date):
    resp = _read_expanded_api(org_id, start_date)
    resp = _filter_response(resp)
    with open("courtreserve_response.json", "w") as f:
        f.write(json.dumps(resp, indent=2))
    return resp


def main():
    logging.basicConfig(level="DEBUG")
    org_id = 10243  # McCarren Park
    start_date = "2024-10-26"
    resp = fetch_courts(org_id, start_date)
    print(resp)


if __name__ == "__main__":
    main()
