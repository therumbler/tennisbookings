from dataclasses import dataclass, asdict
from datetime import datetime
import logging


logger = logging.getLogger(__name__)


@dataclass
class TimeSlot:
    location_name: str
    court_name: str
    datetime_str: str
    datetime_obj: datetime
    booking_url: str
    is_booked: bool = False
    key: str = None

    def __post_init__(self):
        self.key = f"{self.location_name}-{self.court_name}-{self.datetime_str}"

    def asdict(self):
        return asdict(self)
