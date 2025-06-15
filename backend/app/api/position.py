# backend/app/api/position.py
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.database import SessionLocal
# from ..services.position import get_positions # this is the old one
from ..services.position import get_positions_with_pnl as get_positions
from ..schemas.position import PositionOut

router = APIRouter(tags=["positions"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get(
    "/positions",
    response_model=List[PositionOut],
    summary="Current net positions per firm & symbol",
)
def list_positions(
        firm_id: Optional[int] = None,
        symbol: Optional[str] = None,
        db: Session = Depends(get_db),
):
    """
    Optional query params:
      * **firm_id** – filter to one firm
      * **symbol**  – filter to one symbol
    """
    data = get_positions(db)
    if firm_id is not None:
        data = [p for p in data if p["firm_id"] == firm_id]
    if symbol is not None:
        data = [p for p in data if p["symbol"] == symbol]
    return data