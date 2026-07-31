from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db

DbSession = Annotated[Session, Depends(get_db)]

LimitParam = Annotated[int, Query(ge=1, le=500)]
OffsetParam = Annotated[int, Query(ge=0)]
