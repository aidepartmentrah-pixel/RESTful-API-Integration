from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    doctor_id: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Not exposed in the Doctor response schema (OpenAPI v1.1), but searchable
    # via `q` -- "matches ... full name, first name, father name, last name,
    # assistant number, or the numeric id rendered as text".
    first_name: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    father_name: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    last_name: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    assistant_number: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    specialty_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    specialty_name: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)

    # Always null today -- no department is modelled on Doctor; kept only for
    # contract compatibility (OpenAPI v1.1).
    department_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    department_name: Mapped[str | None] = mapped_column(String(128), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
