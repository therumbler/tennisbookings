import json
import logging

from workers import fetch, Response

from lib.nycgovparks import _get_timeslots_from_html

logger = logging.getLogger(__name__)


async def _fetch_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/ "
    }
    resp = await fetch(url, headers=headers)
    html = await resp.text()
    return html


async def on_fetch(request, env):
    logger.info("Received request: %s", request)
    url = "https://www.nycgovparks.org/tennisreservation/availability/3"
    html = await _fetch_html(url)
    try:
        courts = _get_timeslots_from_html(html, booking_url=url)
    except Exception as ex:
        logger.error("Error fetching courts: %s", ex)
        raise ex
        return Response(
            json.dumps({"error": "Failed to fetch courts"}),
            status=500,
            headers={"Content-Type": "application/json"},
        )

    resp_body = json.dumps([court.asdict() for court in courts])
    return Response(resp_body, headers={"Content-Type": "application/json"})
