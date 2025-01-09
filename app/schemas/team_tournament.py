from typing import List
from pydantic import BaseModel

class Team_in_T(BaseModel):
    tournament_id: int
    team_id:int
    class Config:
        from_attributes = True
