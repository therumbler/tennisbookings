from datetime import datetime
import unittest

from lib.courtreserve import _generate_time_slots, _is_booked
from models.time_slot import TimeSlot


class TestCourtReserve(unittest.TestCase):
    def test_generate_time_slots(self):
        start_date = datetime.now().strftime("%Y-%m-%d")

        slots = _generate_time_slots(start_date)
        assert len(slots) > 0
        assert slots[0].datetime_str[:10] == start_date

    def test_booked_slot_true(self):
        booked_slots = [
            {
                "Start": "2024-11-08T12:00:00Z",
                "End": "2024-11-08T13:30:00Z",
                "CourtLabel": "Court A",
            },
            {
                "Start": "2024-11-08T18:00:00Z",
                "End": "2024-11-08T18:30:00Z",
                "CourtLabel": "Court A",
            },
        ]

        time_slot = TimeSlot(datetime_str="2024-11-08T12:00:00Z")

        assert _is_booked(time_slot, booked_slots) == True

    def test_booked_slot_false(self):
        booked_slots = [
            {
                "Start": "2024-11-08T12:00:00Z",
                "End": "2024-11-08T12:30:00Z",
            },
            {
                "Start": "2024-11-08T18:00:00Z",
                "End": "2024-11-08T18:30:00Z",
            },
        ]

        time_slot = TimeSlot(datetime_str="2024-11-08T15:00:00Z")

        assert _is_booked(time_slot, booked_slots) is False


def test():
    pass


if __name__ == "__main__":
    unittest.main()
