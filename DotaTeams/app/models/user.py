from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import relationship,mapped_column,Mapped
from database.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True,autoincrement=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    profile: Mapped["Profile"] = relationship("Profile", uselist=False, back_populates="user")
    teams_created = relationship("Team", back_populates="creator")
    teams = relationship("Team", secondary="team_members",back_populates="members")
    # User_T:Mapped["User_team"]=relationship("User_team",back_populates="user")
    # team: Mapped["Team"] = relationship("Team",  back_populates="creator")

