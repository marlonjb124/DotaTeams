from typing import List
from pydantic import BaseModel
from ..schemas.user_team import User
from ..schemas.user_team import Team
class TournamentBase(BaseModel):
    name: str
    class Config:
        from_attributes = True
# class TournamentCreate(TournamentBase):
#     creator_id: int

class Tournament(TournamentBase):
    id: int
    creator: User
    teams_in_t : List[Team] = []

    class Config:
        from_attributes = True
class TournamentUpdate(TournamentBase):
    id:int
    name:str|None=None
    