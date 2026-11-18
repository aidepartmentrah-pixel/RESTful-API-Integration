from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ErVisit(Base):
    """ER visit as 3iSoft delivered it (v1.2): served by the separate ER API
    (/his-er/api/er/v1/current-visits, own key) - on meraj in production."""

    __tablename__ = "er_visits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    er_visit_id: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)

    first_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    father_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(128), nullable=True)

    # Timezone-aware. 3iSoft returns it with the server's offset (Asia/Beirut).
    arrival_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    # 3iSoft: gender is the Arabic word (male/female) or a raw code; age in whole
    # years from the birth date; chief_complaint is the free-text attendance notes.
    gender: Mapped[str | None] = mapped_column(String(32), nullable=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chief_complaint: Mapped[str | None] = mapped_column(String(255), nullable=True)
