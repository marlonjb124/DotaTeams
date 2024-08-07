from sqlalchemy import  ForeignKey, Integer, UniqueConstraint,Column,String
from sqlalchemy.orm import relationship
# from sqlalchemy.orm import mapped_column,Mapped
from database.database import Base
from models.tournaments import Tournament
from models.tournaments_teams import TournamentTeam
class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String,unique=True)
    # creator: Mapped[str] = mapped_column(String)
    creator_id = Column(ForeignKey("users.id"))
    creator = relationship("User", back_populates="teams_created", uselist=False)
    members = relationship("User", secondary="team_members",back_populates="teams")
    tournaments = relationship("Tournament",secondary="tournament_teams",back_populates="teams_in_t")
    # Team_U =relationship("User_team",back_populates="team")
    # members = relationship("User", secondary="team_members")
    # __table_args__ = (UniqueConstraint("creator_id"),)
    

# event.listen(P