from typing import List, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

# matching engine + models
from ..matching.engine import match_orders
from ..models.trade import Trade as TradeModel
from ..models.order import Order, OrderStatus

# DB session + schemas
from ..core.database import SessionLocal
from ..schemas.order import OrderIn, OrderOut

router = APIRouter(tags=["orders"])


# ──────────────────────────────  DB dependency  ──────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ────────────────────────────────  endpoints  ────────────────────────────────
@router.post(
    "/orders",
    response_model=OrderOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new order and auto-match",
)
def create_order(payload: OrderIn, db: Session = Depends(get_db)):
    # 1️⃣  insert the new order (but don’t commit yet)
    order = Order(
        firm_id=payload.firm_id,
        symbol=payload.symbol,
        side=payload.side,
        quantity=payload.quantity,
        remaining_qty=payload.quantity,
        price=payload.price,
        status=OrderStatus.OPEN,
    )
    db.add(order)
    db.flush()  # assigns order.id without committing

    # 2️⃣  fetch live (open) orders for the same symbol, including the new one
    live_orders = (
        db.query(Order)
        .filter(
            Order.symbol == order.symbol,
            Order.remaining_qty > 0,
            Order.status == OrderStatus.OPEN,
            )
        .all()
    )

    # 3️⃣  run the matcher and persist any resulting trades
    new_trades = match_orders(live_orders)
    for t in new_trades:
        db.add(
            TradeModel(
                buy_order_id=t.buy_order_id,
                sell_order_id=t.sell_order_id,
                symbol=t.symbol,
                price=t.price,
                quantity=t.quantity,
            )
        )

    # 4️⃣  commit all changes in one shot and refresh the order state
    db.commit()
    db.refresh(order)  # picks up PARTIALLY_FILLED / FILLED status changes
    return order  # OrderOut schema


@router.get(
    "/orders",
    response_model=List[OrderOut],
    summary="List all orders",
)
def list_orders(
        symbol: Optional[str] = None,
        db: Session = Depends(get_db),
):
    q = db.query(Order)
    if symbol:
        q = q.filter(Order.symbol == symbol)
    return q.all()

