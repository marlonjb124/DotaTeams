from typing import List
from pydantic import BaseModel
from schemas.user import User
class Member(BaseModel):
    user_id: int
    team_id:int
    class Config:
        from_attributes = True

