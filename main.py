#!/usr/bin/env python3
from datetime import datetime
import logging

from lib.courtreserve import fetch_courts


def fetch_all_courts():
    """fetch courts from all systems"""
    logging.basicConfig(level="DEBUG")
    org_id = 10243  # McCarren Park
    start_date = datetime.now().strftime("%Y-%m-%d")

    court_reserve_resp = fetch_courts(org_id, start_date)

    return court_reserve_resp


def main():
    """let's kick it all off"""
    resp = fetch_all_courts()
    print(resp["Court #4"])


if __name__ == "__main__":
    main()
