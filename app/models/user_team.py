from sqlalchemy import Boolean, Column, ForeignKey, Integer, String,Float, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.orm import mapped_column,Mapped
from app.database.database import Base

class User_team(Base):
    __tablename__ = "team_members"
    user_id:Mapped[int] = mapped_column(Integer,ForeignKey("users.id",ondelete="CASCADE"), primary_key=True)
    team_id:Mapped[int] = mapped_column(Integer,ForeignKey("teams.id",ondelete="cascade"), primary_key=True)
    # user: Mapped["User"] = relationship("User", back_populates="User_T")
    # team: Mapped["Team"] = relationship("Team", back_populates="Team_U")
    # creator: Mapped[str] = mapped_column(String)
    # __table_args__ = (UniqueConstraint("user_id"),)

