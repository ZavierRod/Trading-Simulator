# backend/app/api/trade.py
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.database import SessionLocal
from ..models.trade import Trade
from ..schemas.trade import TradeOut

router = APIRouter(tags=["trades"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get(
    "/trades",
    response_model=List[TradeOut],
    summary="List trades (cursor-paginated)",
)
def list_trades(
        limit: int = 100,
        cursor: Optional[int] = None,
        db: Session = Depends(get_db),
):
    limit = max(1, min(limit, 1000))
    q = db.query(Trade)
    if cursor is not None:
        q = q.filter(Trade.id < cursor)
    return q.order_by(Trade.id.desc()).limit(limit).all()