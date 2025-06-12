from datetime import datetime
from pydantic import BaseModel


class StrategyIn(BaseModel):
    firm_id: int
    code: str


class StrategyOut(BaseModel):
    id: int
    firm_id: int
    created_at: datetime
    code: str
    class Config:
        orm_mode=True
