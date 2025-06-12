from datetime import datetime
from pydantic import Field
from pydantic import BaseModel

class OrderIn(BaseModel):
    firm_id: int
    symbol: str
    side: str
    quantity: int = Field(gt=0, description="Must be a positive integer you twat")
    price: float

class OrderOut(BaseModel):
    id: int
    firm_id: int
    symbol: str
    side: str
    quantity: int
    price: float
    created_at: datetime
    class Config:
        orm_mode = True