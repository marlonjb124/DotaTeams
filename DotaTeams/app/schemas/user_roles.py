
from pydantic import BaseModel

class User_rol(BaseModel):
    user_id: int
    rol_id:int
    class Config:
        from_attributes = True

