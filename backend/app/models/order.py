import enum

from ..core.database import Base
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func, Enum as SAEnum

class OrderStatus(str, enum.Enum):
    OPEN = "open"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(Integer, ForeignKey("firms.id"), index=True, nullable=False)
    symbol = Column(String, index=True, nullable=False)
    side = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    remaining_qty = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    status = Column(
        SAEnum(OrderStatus, name="order_status"),
        nullable=False,
        server_default="open"
    )
