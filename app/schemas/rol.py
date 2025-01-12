
from pydantic import BaseModel
class Rol(BaseModel):
    rol: str
    id:int
    class Config:
        from_attributes = True
class Rol_create(BaseModel):
    rol:str
    class Config:
        from_attributes = True