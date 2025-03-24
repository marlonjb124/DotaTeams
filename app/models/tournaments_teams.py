from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.database.database import Base

class TournamentTeam(Base):
    __tablename__ = "tournament_teams"

    tournament_id = Column(Integer, ForeignKey("tournaments.id",ondelete="CASCADE"), primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id",ondelete="CASCADE"), primary_key=True)