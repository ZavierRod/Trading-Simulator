# backend/app/api/trade.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# import your shared DB session factory
from ..core.database import SessionLocal
from ..models.trade import Trade
# import your ORM model and Pydantic schemas
from ..schemas.trade import TradeOut
from ..matching.engine import match_orders
from ..models.order import Order
router = APIRouter(tags=["trades"])

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
    "/trades",
    response_model=List[TradeOut],
    status_code=status.HTTP_201_CREATED,
    summary="Match the orders and create trades",
)
def execute_match(
        db: Session = Depends(get_db),
):

    all_orders = db.query(Order).all()
    matched_trades = match_orders(all_orders)
    new_trades = []
    for trade in matched_trades:
        db_trade = Trade(
            buy_order_id=trade.buy_order_id,
            sell_order_id=trade.sell_order_id,
            symbol=trade.symbol,
            quantity=trade.quantity,
            price=trade.price
        )
        db.add(db_trade)
        new_trades.append(db_trade)
    db.commit()
    for t in new_trades:
        db.refresh(t)
    return new_trades or [{"message": "No trades matched"}]

@router.get(
    "/trades",
    response_model=List[TradeOut],
    summary="List all trades",
)
def list_trades(db: Session = Depends(get_db)):
    return db.query(Trade).all()