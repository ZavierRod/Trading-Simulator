from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Matching engine and Trade model
from ..matching.engine import match_orders
from ..models.trade import Trade as TradeModel

# import your shared DB session factory
from ..core.database import SessionLocal
# import your ORM model and Pydantic schemas
from ..models.order import Order, OrderStatus
from ..schemas.order import OrderIn, OrderOut

router = APIRouter(tags=["orders"])

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
    "/orders",
    response_model=OrderOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new order",
)
def create_order(
        payload: OrderIn,
        db: Session = Depends(get_db),
):

    order = Order(firm_id=payload.firm_id,
                      symbol=payload.symbol,
                      side=payload.side,
                      quantity=payload.quantity,
                        remaining_qty=payload.quantity,
                        status=OrderStatus.OPEN,
                      price=payload.price,
                  )
    db.add(order)
    db.commit()
    db.refresh(order)
    # ------------------------------------------------------------------
    # Run the matching engine whenever a new order is created
    open_orders = db.query(Order).filter(Order.quantity > 0).all()
    new_trades = match_orders(open_orders)

    for trade in new_trades:
        # `trade` is expected to be a simple object (or dict‑like) with the
        # attributes produced by `engine.match_orders`.  Adapt the field names
        # below if your Trade model differs.
        db.add(
            TradeModel(
                buy_order_id=trade.buy_order_id,
                sell_order_id=trade.sell_order_id,
                symbol=trade.symbol,
                price=trade.price,
                quantity=trade.quantity,
            )
        )
    if new_trades:
        db.commit()
    # ------------------------------------------------------------------
    return order

@router.get(
    "/orders",
    response_model=List[OrderOut],
    summary="List all orders",
)
def get_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()



