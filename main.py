#!/usr/bin/env python3
import logging

from tennisbookings import fetch_courts_and_notify

logger = logging.getLogger(__name__)


def main():
    """let's kick it all off"""
    logging.basicConfig(level="INFO")
    fetch_courts_and_notify()


if __name__ == "__main__":
    main()
