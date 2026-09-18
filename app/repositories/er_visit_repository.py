from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.er_visit import ErVisit


def list_current_visits(db: Session) -> list[ErVisit]:
    # Deliberately no limit/offset -- see requirement.md section 4:
    # departure-detection requires a complete snapshot on every poll.
    stmt = select(ErVisit).order_by(ErVisit.arrival_time.asc())
    return list(db.execute(stmt).scalars().all())
