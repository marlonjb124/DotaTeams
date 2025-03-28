
from typing import TYPE_CHECKING,List,ForwardRef
from pydantic import BaseModel,ConfigDict
from app.schemas.rol import Rol,Rol_create
# from app.schemas.rol import DefaultRoles
    


class UserBase(BaseModel):
    email: str

    class Config:
        from_attributes = True
        # arbitrary_types_allowed=True
        
        
class UserCreate(UserBase):
    password: str
    # rol:List["Rol_create"]=[Rol_create(rol=DefaultRoles.BASIC_USER_ROL)]
    class Config:
        from_attributes = True

class User(UserBase):
    id: int
    is_active: bool
    rol:List[Rol]=[]
    class Config:
        from_attributes = True
class UserReturn(User):
    teams:list["TeamBase"] = []
    teams_created:list["TeamBase"] = []
class TeamBase(BaseModel):
    name: str
    id: int
    description:str|None = None
    class Config:
        from_attributes = True
        # arbitrary_types_allowed = True
class TeamCreate(BaseModel):
    name:str
    description:str
class TeamReturn(TeamBase):
    creator: User
    members: List[User] = []  
    tournaments:List["Tournament"] =[]
 
class Team(TeamBase):
    pass


    # profile:ProfileReturn
class Member(BaseModel):
    user_id: int
    team_id:int
    class Config:
        from_attributes = True
        # arbitrary_types_allowed = True

class Token(BaseModel):
    access_token: str
    token_type: str
class TokenData(BaseModel):
    username: str | None = None
    
    class Config:
        from_attributes = True

class TeamUpdateSchema(BaseModel):
    id:int
    name: str|None = None
