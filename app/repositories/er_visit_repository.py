from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.er_visit import ErVisit


def list_current_visits(db: Session) -> list[ErVisit]:
    # Deliberately no limit/offset -- see requirement.md section 4:
    # departure-detection requires a complete snapshot on every poll.
    # 3iSoft: earliest arrival first; equal times by visit id.
    stmt = select(ErVisit).order_by(
        ErVisit.arrival_time.asc(), func.length(ErVisit.er_visit_id), ErVisit.er_visit_id
    )
    return list(db.execute(stmt).scalars().all())
