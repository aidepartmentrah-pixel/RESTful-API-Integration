from sqlalchemy import Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    patient_id: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)

    first_name_ar: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    first_name_en: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    father_name_ar: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    father_name_en: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    last_name_ar: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    last_name_en: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)

    birth_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sex: Mapped[str | None] = mapped_column(String(32), nullable=True)
    encounter_type: Mapped[str | None] = mapped_column(String(32), nullable=True)

    @property
    def first_name(self) -> str | None:
        """English when stored, otherwise Arabic -- OpenAPI v1.1 Patient.first_name rule."""
        return self.first_name_en or self.first_name_ar

    @property
    def last_name(self) -> str | None:
        """English when stored, otherwise Arabic -- OpenAPI v1.1 Patient.last_name rule."""
        return self.last_name_en or self.last_name_ar

    @property
    def full_name(self) -> str | None:
        """Arabic first+father+last joined with single spaces, blanks skipped;
        null only if all three are blank -- OpenAPI v1.1 Patient.full_name rule."""
        parts = [p for p in (self.first_name_ar, self.father_name_ar, self.last_name_ar) if p]
        return " ".join(parts) if parts else None
