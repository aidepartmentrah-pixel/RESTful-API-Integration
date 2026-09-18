from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ErVisit(Base):
    """PROPOSED v1.2 resource -- see
    versions/v1.2/requirements/5-er-current-visits-hcopilot/requirement.md.
    Sourced today from a separate non-JSON system ("meraj"); modelled here
    only so HCopilot can develop against a stand-in while that ask is
    pending with the vendor."""

    __tablename__ = "er_visits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    er_visit_id: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)

    first_name: Mapped[str] = mapped_column(String(128), nullable=False)
    father_name: Mapped[str] = mapped_column(String(128), nullable=False)
    last_name: Mapped[str] = mapped_column(String(128), nullable=False)

    # Timezone-aware; stored as the vendor is assumed (not confirmed) to
    # write it -- UTC+3. See requirement.md open item 1.
    arrival_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    # All three are open items in the requirement doc -- shape unconfirmed,
    # so kept plain/nullable rather than guessed at.
    gender: Mapped[str | None] = mapped_column(String(32), nullable=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chief_complaint: Mapped[str | None] = mapped_column(String(255), nullable=True)
