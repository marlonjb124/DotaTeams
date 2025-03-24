
from pydantic import BaseModel
from datetime import datetime

from app.models import invitacion
class InvitacionBase(BaseModel):
    team_id:int
    invited_user_id:int
class InvitacionCreate(InvitacionBase):
    # user_id:int
    pass
    class Config:
        from_attributes = True
class InvitacionResponse(InvitacionBase):
    id:int
    status:str = "pendiente"
    token:str
    expToken:datetime
    class Config:
        from_attributes=True