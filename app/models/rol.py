from sqlalchemy import Integer,Column,String
from sqlalchemy.orm import relationship,mapped_column,Mapped
from app.database.database import Base

class Rol(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True,autoincrement=True)
    rol = Column(String,unique=True,nullable=False)
    useRol=relationship("User",secondary="user_roles",back_populates="rol")