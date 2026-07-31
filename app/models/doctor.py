from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    doctor_id: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    specialty_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    specialty_name: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    department_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    department_name: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
