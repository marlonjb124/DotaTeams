from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship
from database.database import Base

class TournamentTeam(Base):
    __tablename__ = "tournament_teams"

    tournament_id = Column(Integer, ForeignKey("tournaments.id"), primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id"), primary_key=True)