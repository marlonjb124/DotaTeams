# from calendar import c
from enum import Enum
from pydantic import BaseModel
class Rol(BaseModel):
    rol: str
    id:int
    class Config:
        from_attributes = True
class Rol_create(BaseModel):
    rol:str
    class Config:
        from_attributes = True
        
class DefaultRoles(str, Enum):
    SUPER_ADMIN_ROL = "Super_admin"
    ADMIN_ROL = "Admin"
    TEAM_GESTOR_ROL = "Team_gestor"
    BASIC_USER_ROL = "Basic_user"
    
    