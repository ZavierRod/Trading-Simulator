
#schemas/trade.py
from datetime import datetime
from pydantic import BaseModel

class TradeOut(BaseModel):
    id: int
    buy_order_id: int
    sell_order_id: int
    symbol: str
    quantity: int
    price: float
    executed_at: datetime
    class Config:
        orm_mode = True