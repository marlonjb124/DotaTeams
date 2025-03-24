from typing import List,TYPE_CHECKING,ForwardRef
from pydantic import BaseModel


if TYPE_CHECKING:
    from app.schemas.user_team import User
    from app.schemas.user_team import Team
    
# UserRef=ForwardRef("User")
class TournamentBase(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True
# class TournamentCreate(TournamentBase):
#     creator_id: int

class Tournament(TournamentBase):
    creator: "User"

class TournamentUpdate(TournamentBase):
    name:str|None=None
    
class TournamentPublicComplete(TournamentBase):
    id: int
    creator: "User"
    teams_in_t : List["Team"] = []
    
# TournamentPublicComplete.model_rebuild()