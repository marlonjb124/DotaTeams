from sqlalchemy import  Column, ForeignKey, Integer, String,UniqueConstraint,DateTime
from app.database.database import Base
from datetime import datetime
class Invitacion(Base):
    __tablename__ = "invitaciones"
    id = Column(Integer, primary_key=True)
    token = Column(String)
    team_id = Column(Integer, ForeignKey("teams.id"))
    invited_user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="pendiente") 
    expToken =  Column(DateTime,default=datetime.now())
    

    __table_args__ = (UniqueConstraint("invited_user_id"),)