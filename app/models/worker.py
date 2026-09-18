from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Worker(Base):
    __tablename__ = "workers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    employee_id: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    job_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    job_title: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    department_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    department_name: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    section_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    section_name: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    administration_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    administration_name: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)

    is_manager: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
