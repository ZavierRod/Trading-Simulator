from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import text, Column, Integer, String
from .core.database import Base, engine, SessionLocal
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .models.firm import Firm
app = FastAPI()

class FirmIn(BaseModel):
    name: str

class FirmOut(BaseModel):
    id: int
    name: str
    class Config:
        orm_model = True



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/firm", response_model=FirmOut)
def create_firm(payload: FirmIn, db: Session = Depends(get_db)):
    firm = Firm(name=payload.name)
    db.add(firm)
    db.commit()
    db.refresh(firm)
    return firm
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status: ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

