from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# import your shared DB session factory
from ..core.database import SessionLocal
from ..schemas.leaderboard import LeaderboardEntry

# import your ORM model and Pydantic schemas

from ..models.firm import Firm
from ..models.trade import Trade

router = APIRouter(tags=["leaderboard"])

def get_db():
    """
    Dependency to provide a SQLAlchemy DB session, closing it after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get(
    '/leaderboard',
    response_model=List[LeaderboardEntry],
    summary='Computer Profit and Loss for each firm'
)
def create_leaderboard(db: Session = Depends(get_db)):
    all_firms = db.query(Firm).all()
    leaderboard_entries = []

    for firm in all_firms:
        # sell_trades = [trade for trade in firm if trade.sell_order_id == firm.id]
        # buy_trades = [trade for trade in firm if trade.buy_order_id == firm.id]
        sell_trades = db.query(Trade).filter(Trade.sell_order_id == firm.id).all()
        buy_trades = db.query(Trade).filter(Trade.buy_order_id  == firm.id).all()

        revenue = 0.0
        cost = 0.0
        for trade in sell_trades:
            revenue += trade.price * trade.quantity
        for trade in buy_trades:
            cost += trade.price * trade.quantity

        profit = revenue - cost

        entry = LeaderboardEntry(
            firm_id= firm.id,
            firm_name= firm.name,
            revenue=revenue,
            cost=cost,
            profit=profit
        )
        leaderboard_entries.append(entry)
    leaderboard_entries.sort(key=lambda x: x.profit, reverse=True)
    return leaderboard_entries
