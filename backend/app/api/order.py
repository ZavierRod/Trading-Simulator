from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# import your shared DB session factory
from ..core.database import SessionLocal
# import your ORM model and Pydantic schemas
from ..models.order import Order
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
                      price=payload.price,)
    db.add(order)
    db.commit()
    db.refresh(order)
    return order

@router.get(
    "/orders",
    response_model=List[OrderOut],
    summary="List all orders",
)
def get_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()



