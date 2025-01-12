from pydantic import BaseModel,Field
from schemas.rol import Rol,Rol_create
from typing import List
class UserBase(BaseModel):
    email: str
    

class UserCreate(UserBase):
    password: str
    rol:List[Rol_create]=[Rol_create(rol="Guest")]
    

class User(UserBase):
    id: int
    is_active: bool
    rol:List[Rol]=[]
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    