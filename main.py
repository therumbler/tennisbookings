#!/usr/bin/env python3
from datetime import datetime
import logging

# from lib.courtreserve import fetch_courts
from lib.nycgovparks import fetch_available_courts


def fetch_all_courts():
    """fetch courts from all systems"""
    logging.basicConfig(level="INFO")
    # org_id = 10243  # McCarren Park
    # start_date = datetime.now().strftime("%Y-%m-%d")

    # court_reserve_resp = fetch_courts(org_id, start_date)
    court_id = 11
    nyc_gov_parks_resp = fetch_available_courts(court_id)
    return nyc_gov_parks_resp


def main():
    """let's kick it all off"""
    resp = fetch_all_courts()
    print(resp)


if __name__ == "__main__":
    main()
