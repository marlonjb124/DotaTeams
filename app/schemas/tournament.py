# from __future__ import annotations
from typing import List,TYPE_CHECKING
from pydantic import BaseModel


    
    

class TournamentBase(BaseModel):   
    name: str
    
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
class TournamentCreate(TournamentBase):
    pass



class TournamentUpdate(TournamentBase):
    id:int
    name:str|None=None
    
class TournamentPublicComplete(TournamentBase):
    id: int
    creator: "User"
    teams_in_t : List["Team"] = []
class Tournament(TournamentBase):
    id: int
    creator: "User"
    
    

