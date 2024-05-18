from typing import List
from pydantic import BaseModel
from schemas.user import User
from schemas.team import Team
class TournamentBase(BaseModel):
    name: str

# class TournamentCreate(TournamentBase):
#     creator_id: int

class Tournament(TournamentBase):
    id: int
    creator: User
    teams_in_t : List[Team] = []

    class Config:
        from_attributes = True