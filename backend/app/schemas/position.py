# backend/app/schemas/position.py
from pydantic import BaseModel, ConfigDict
from typing import Optional

class PositionOut(BaseModel):
    firm_id: int
    symbol: str
    net_qty: int
    avg_price: Optional[float]
    last_price: Optional[float]
    pnl: float
    model_config = ConfigDict(from_attributes=True)