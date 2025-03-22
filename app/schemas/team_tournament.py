from typing import List
from pydantic import BaseModel
class Team_in_T(BaseModel):
    tournament_id: int
    team_id:int
    class Config:
        from_attributes = True
# class TeamPublicComplete(TeamBase):
#     id: int
#     description:str|None = None
#     creator: User
#     members: List[User] = []  
#     tournaments:List