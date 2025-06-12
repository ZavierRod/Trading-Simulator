# backend/app/main.py

from fastapi import FastAPI, HTTPException
from sqlalchemy import text

# Shared database setup
from backend.app.core.database import Base, engine

# Import your firm router (defined in api/firm.py)
from backend.app.api.firm import router as firm_router
from .api.order import router as order_router
from .api.trade import router as trade_router
from .api.leaderboard import router as leaderboard_router
from .api.strategy import router as strategy_router
app = FastAPI()

# Create all tables on startup (dev convenience)
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

# Mount the firm, order, and trade endpoints under /api
app.include_router(firm_router, prefix="/api")
app.include_router(order_router, prefix="/api")
app.include_router(trade_router, prefix="/api")
app.include_router(leaderboard_router, prefix="/api")
app.include_router(strategy_router, prefix="/api")

# Simple root endpoint
@app.get("/")
async def root():
    return {"message": "Hello World"}

# Health-check that also pings the database
@app.get("/health")
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
