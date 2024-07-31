from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship
from database.database import Base

class User_rol(Base):
    __tablename__ = "user_roles"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    rol_id = Column(Integer, ForeignKey("roles.id"),primary_key=True,default=2)