from typing import List
from pydantic import BaseModel
from schemas.user import User
class TeamBase(BaseModel):
    name: str

class TeamCreate(TeamBase):
    creator_id: int

class Team(TeamBase):
    id: int
    creator: User
    members: List[User] = []

    class Config:
        from_attributes = True