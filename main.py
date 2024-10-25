#!/usr/bin/env python3
from lib.courtreserve import fetch_courts


def fetch_all_courts():
    org_id = 10243  # McCarren Park
    start_date = "2024-10-25"
    court_reserve_resp = fetch_courts(org_id, start_date)
    print(court_reserve_resp)


def main():
    fetch_all_courts()


if __name__ == "__main__":
    main()
