from sqlalchemy import Column, Integer, String
from ..core.database import Base

class Firm(Base):
    __tablename__ = 'firms'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
