import os
from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from sandbox_runner.runner import run_strategy as runner_run_strategy


# import your shared DB session factory
from ..core.database import SessionLocal
# import your ORM model and Pydantic schemas
from ..models.strategy import Strategy
from ..schemas.strategy import StrategyIn, StrategyOut

router = APIRouter(tags=["strategies"])

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
    "/strategies",
    response_model=StrategyOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new strategy",
)
def create_strategy(
        payload: StrategyIn,
        db: Session = Depends(get_db)):
    strategy = Strategy(firm_id=payload.firm_id, code=payload.code)
    db.add(strategy)
    db.commit()
    db.refresh(strategy)
    return strategy


@router.get(
    "/strategies",
    response_model=List[StrategyOut],
    summary="List all strategies"
)
def list_strategies(db: Session = Depends(get_db)):
    return db.query(Strategy).all()

@router.get(
    "/strategies/{strategy_id}",
    response_model=StrategyOut,
    summary="Get a single strategy by ID",
)
def get_strategy(
        strategy_id: int,
        db: Session = Depends(get_db),
):
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail=f"Strategy {strategy_id} not found")
    return strategy


@router.post(
    "/strategies/{strategy_id}/run",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Run a strategy",
)
def run_strategy(
    strategy_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail=f"Strategy {strategy_id} not found")
    background_tasks.add_task(
        runner_run_strategy,
        strategy_id,
        "/app/data/test_feed.json",
    )
    return {"status": "runner started"}
