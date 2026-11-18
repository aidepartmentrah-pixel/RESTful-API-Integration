from datetime import datetime
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, field_serializer

# 3iSoft v1.2: arrival_time carries "the server's time-zone offset". The ER
# server is in Beirut, so the offset is +02:00 in winter and +03:00 in summer.
_SERVER_TZ = ZoneInfo("Asia/Beirut")


class ErVisit(BaseModel):
    """GET /his-er/api/er/v1/current-visits item, as 3iSoft delivered it.
    Every field is always present; null when it has no value."""

    model_config = ConfigDict(from_attributes=True)

    er_visit_id: str
    first_name: str | None = None
    father_name: str | None = None
    last_name: str | None = None
    arrival_time: datetime
    gender: str | None = None
    age: int | None = None
    chief_complaint: str | None = None

    @field_serializer("arrival_time")
    def _serialize_arrival_time(self, value: datetime) -> str:
        # Postgres (timestamptz) returns an aware UTC instant: convert it.
        # SQLite (unit tests only) returns a naive value holding the wall-clock
        # digits as stored: treat those as Beirut local time.
        if value.tzinfo is None:
            value = value.replace(tzinfo=_SERVER_TZ)
        return value.astimezone(_SERVER_TZ).replace(microsecond=0).isoformat()


class ErVisitListResponse(BaseModel):
    success: bool = True
    items: list[ErVisit]
    total: int
