from sqlalchemy.orm import Session

from app.models.er_visit import ErVisit
from app.repositories import er_visit_repository


def list_current_visits(db: Session) -> list[ErVisit]:
    return er_visit_repository.list_current_visits(db)
