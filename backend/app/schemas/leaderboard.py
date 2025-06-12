from pydantic import BaseModel

class LeaderboardEntry(BaseModel):
    firm_id: int
    firm_name: str
    revenue: float
    cost: float
    profit: float
    class Config:
        orm_mode=True