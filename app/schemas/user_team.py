from typing import List
from pydantic import BaseModel
from ..schemas.rol import Rol,Rol_create


class UserBase(BaseModel):
    email: str
    class Config:
        from_attributes = True

class UserCreate(UserBase):
    password: str
    rol:List[Rol_create]=[Rol_create(rol="Guest")]
    class Config:
        from_attributes = True

class User(UserBase):
    id: int
    is_active: bool
    rol:List[Rol]=[]
    class Config:
        from_attributes = True
class TeamBase(BaseModel):
    name: str
class Team(TeamBase):
    id: int
    description:str|None = None
    creator: User
    members: List[User] = []  
class UserReturn(User):
    teams:list[Team] = []
    teams_created:list[Team] = []
    # profile:ProfileReturn
class Member(BaseModel):
    user_id: int
    team_id:int
    class Config:
        from_attributes = True



class Token(BaseModel):
    access_token: str
    token_type: str
class TokenData(BaseModel):
    username: str | None = None
    



# class TeamCreate(TeamBase):
#     creator_id: int
    # tournaments: List[ForwardRef("Tournament")]s
    class Config:
        from_attributes = True

class TeamUpdateSchema(BaseModel):
    id:int
    name: str|None = None

