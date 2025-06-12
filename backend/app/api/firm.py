# backend/app/api/firm.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# import your shared DB session factory
from ..core.database import SessionLocal
# import your ORM model and Pydantic schemas
from ..models.firm import Firm
from ..schemas.firm import FirmIn, FirmOut

router = APIRouter(tags=["firms"])

def get_db():
    """
    Dependency to provide a SQLAlchemy DB session, closing it after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post(
    "/firm",
    response_model=FirmOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new firm",
)
def create_firm(
        payload: FirmIn,
        db: Session = Depends(get_db),
):
    # Check uniqueness manually (optional)
    existing = db.query(Firm).filter(Firm.name == payload.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Firm '{payload.name}' already exists."
        )

    firm = Firm(name=payload.name)
    db.add(firm)
    db.commit()
    db.refresh(firm)
    return firm
