from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class TimeSlot:
    location_name: str
    court_name: str
    datetime_str: str
    datetime_obj: datetime
    booking_url: str
    is_booked: bool = False

    def asdict(self):
        return asdict(self)
