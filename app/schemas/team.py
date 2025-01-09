
from pydantic import BaseModel
from typing import List,ForwardRef
from schemas.user import User
# from schemas.tournament import Tournament

class TeamBase(BaseModel):
    name: str

# class TeamCreate(TeamBase):
#     creator_id: int

class Team(TeamBase):
    id: int
    description:str|None = None
    creator: User
    members: List[User] = []
    # tournaments: List[ForwardRef("Tournament")]s
    class Config:
        from_attributes = True
class TeamUpdateSchema(BaseModel):
    id:int
    name: str|None = None

