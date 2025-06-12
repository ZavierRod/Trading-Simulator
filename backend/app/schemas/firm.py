from pydantic import BaseModel



class FirmIn(BaseModel):
    name: str

class FirmOut(BaseModel):
    id: int
    name: str
    class Config:
        orm_mode = True

