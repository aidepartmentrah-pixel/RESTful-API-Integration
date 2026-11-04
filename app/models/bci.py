from sqlalchemy import JSON, Boolean, Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class BciPatient(Base):
    """PROPOSED v1.3 resource -- see
    versions/v1.3/requirements/2-bci-radiology-patient/requirement.md.
    Kept in its own table, apart from `patients`, so the Directory's data
    and tests are unaffected. Invented test data only (mrn 9999.*)."""

    __tablename__ = "bci_patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mrn: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)

    first_name_ar: Mapped[str | None] = mapped_column(String(128), nullable=True)
    father_name_ar: Mapped[str | None] = mapped_column(String(128), nullable=True)
    last_name_ar: Mapped[str | None] = mapped_column(String(128), nullable=True)
    mother_name_ar: Mapped[str | None] = mapped_column(String(128), nullable=True)
    first_name_en: Mapped[str | None] = mapped_column(String(128), nullable=True)
    father_name_en: Mapped[str | None] = mapped_column(String(128), nullable=True)
    last_name_en: Mapped[str | None] = mapped_column(String(128), nullable=True)
    mother_name_en: Mapped[str | None] = mapped_column(String(128), nullable=True)

    birth_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    sex: Mapped[str | None] = mapped_column(String(32), nullable=True)
    nationality: Mapped[str | None] = mapped_column(String(64), nullable=True)
    id_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    has_allergy: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # [{"number": "...", "owner": "..."}]
    phones: Mapped[list] = mapped_column(JSON, nullable=False, default=list)


class BciVisit(Base):
    """PROPOSED v1.3 resource -- see
    versions/v1.3/requirements/1-bci-radiology-visits-today/requirement.md.
    The mock holds only a clock time ("HH:MM", Asia/Beirut) and treats every
    stored visit as today's: the date is added when the mock answers, so the
    test data never goes stale."""

    __tablename__ = "bci_visits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    visit_id: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    mrn: Mapped[str] = mapped_column(
        String(64), ForeignKey("bci_patients.mrn"), nullable=False, index=True
    )
    visit_clock: Mapped[str] = mapped_column(String(5), nullable=False)
    visit_kind: Mapped[str | None] = mapped_column(String(16), nullable=True)
    doctor_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
