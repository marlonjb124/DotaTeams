
from pydantic import BaseModel
class Rol(BaseModel):
    rol: str
    id:int
    class Config:
        from_attributes = True