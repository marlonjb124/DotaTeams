
from pydantic import BaseModel
class Invitacion(BaseModel):
    # user_id:int
    
    team_id:int
    invited_user_id:int
    status:str = "pendiente"

    class Config:
        from_attributes = True
class Invitacion_Response(Invitacion):
    token:str
    class Config:
        from_attributes=True