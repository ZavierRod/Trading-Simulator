# models/trade.py

from ..core.database import Base
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func

class Trade(Base):
    __tablename__ = "trades"
    id = Column(Integer, primary_key=True, index=True)
    buy_order_id = Column(Integer, ForeignKey("orders.id"), index=True, nullable=False)
    sell_order_id = Column(Integer, ForeignKey("orders.id"), index=True, nullable=False)
    symbol = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    executed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)