from dataclasses import dataclass, asdict


@dataclass
class TimeSlot:
    court_name: str
    datetime_str: str
    is_booked: bool = False

    def asdict(self):
        return asdict(self)
