from datetime import date
from pydantic import BaseModel


class TimelineDates(BaseModel):
    depart_date: date
    return_date: date | None


class TimelineStep(BaseModel):
    phase: str  # pre_departure / check_in / departure_day / arrival / stay / post_trip
    active: bool
    title: str
    description: str
    actions: list[str]  # actions "symboliques" que le frontend mappe vers des pages/components


class TimelineResponse(BaseModel):
    booking_id: str
    destination: str
    origin: str
    trip_type: str
    cabin: str
    status: str  # current phase
    dates: TimelineDates
    steps: list[TimelineStep]
