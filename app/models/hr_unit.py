from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

HR_LEVELS = ("administration", "section", "department")


class HrUnit(Base):
    """A unit of the HR organisational tree (3iSoft v1.2 /hr-workers).

    Three levels, top to bottom: administration (ادارة) > section (دائرة)
    > department (قسم). parent_unit_id points one level up.
    """

    __tablename__ = "hr_units"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    unit_id: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    level: Mapped[str] = mapped_column(String(32), nullable=False)
    parent_unit_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
