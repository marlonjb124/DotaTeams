
from typing import Annotated
from fastapi import APIRouter, HTTPException,Depends
from database.database import SessionLocal
from sqlalchemy.orm import Session
from models.user import User as UserModel
from schemas.user import User as UserSchema
from controllers import userController
from models.tournaments import Tournament
from models.tournaments_teams import TournamentTeam
from schemas.tournament import TournamentBase
from schemas.team import Team,TeamBase 
from schemas.team_tournament import Team_in_T
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

tournament_router = APIRouter(prefix="/Tournaments",tags=["Tournaments"])
@tournament_router.post("/CreateTournament")
async def create_tournament(current_user: Annotated[UserSchema, Depends(userController.require_role("Admin"))],tournamentShema : TournamentBase,db:Session = Depends(get_db)):
    userM =UserModel(**current_user.model_dump(exclude="rol"))
    newT = Tournament(name=tournamentShema.name,creator_id =userM.id)
    db.add(newT)
    db.commit()
    db.refresh(newT)
    return TournamentBase(**newT.__dict__)
@tournament_router.post("/add_Team_Tournament/{tournament_id}")
async def add_team_tournament(team_tournament:Team_in_T,user:UserSchema = Depends(userController.require_role("Admin")),db:Session=Depends(get_db)):
    # user_model= db.query(UserModel).filter(UserModel.id == user.id)
    tournament = db.query(Tournament).filter(Tournament.id == team_tournament.tournament_id).first()
    tournament_team_model = TournamentTeam(tournament_id=team_tournament.tournament_id,team_id =team_tournament.team_id)
    db.add(tournament_team_model)
    db.commit()
    db.refresh(tournament_team_model)
    
    
    return tournament.teams_in_t, Team_in_T(**tournament_team_model.__dict__)