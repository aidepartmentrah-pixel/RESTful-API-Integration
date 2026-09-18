from datetime import datetime, timedelta, timezone

from pydantic import BaseModel, ConfigDict, field_serializer

# Assumed offset for the ER source system, per requirement.md open item 1 --
# unconfirmed by the vendor. Postgres stores/returns timestamptz values as
# UTC regardless of what offset was written; this serializer converts back
# to the assumed +03:00 for display so the mock's output matches the format
# documented in versions/v1.2/Hospital_Directory_API_OpenAPI_v1.2.yaml,
# rather than silently drifting to a bare UTC "Z" suffix.
_ASSUMED_ER_TZ = timezone(timedelta(hours=3))


class ErVisit(BaseModel):
    """PROPOSED v1.2 resource -- see
    versions/v1.2/requirements/5-er-current-visits-hcopilot/requirement.md."""

    model_config = ConfigDict(from_attributes=True)

    er_visit_id: str
    first_name: str
    father_name: str
    last_name: str
    arrival_time: datetime
    gender: str | None = None
    age: int | None = None
    chief_complaint: str | None = None

    @field_serializer("arrival_time")
    def _serialize_arrival_time(self, value: datetime) -> str:
        # Postgres (timestamptz) always returns a UTC-aware instant, so
        # .astimezone() correctly converts it to the assumed display offset.
        # SQLite (used only by the fast unit-test suite) has no timezone
        # storage and hands back a naive datetime holding the original
        # wall-clock digits as-fed -- .astimezone() on a naive value would
        # wrongly reinterpret those digits as this machine's local time, so
        # that case is tagged with the assumed offset directly instead.
        if value.tzinfo is None:
            return value.replace(tzinfo=_ASSUMED_ER_TZ).isoformat()
        return value.astimezone(_ASSUMED_ER_TZ).isoformat()


class ErVisitListResponse(BaseModel):
    success: bool = True
    items: list[ErVisit]
    total: int
