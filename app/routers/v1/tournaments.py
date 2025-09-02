import sqlalchemy
from typing import List
from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse, Response
import sqlalchemy.exc
from app.database.database import SessionLocal
from sqlalchemy.orm import Session
from app.models.user import User as UserModel
from app.schemas.user_team import User as UserSchema
from app.controllers import userController
from app.models.tournaments import Tournament as TournamentModel
from app.models.tournaments_teams import TournamentTeam
from app.models.team import Team as Team_Model
from app.schemas.tournament import TournamentCreate, Tournament, TournamentPublicComplete, TournamentUpdate
from app.schemas.user_team import Team, TeamBase 
from app.schemas.team_tournament import Team_in_T
from app.schemas.rol import DefaultRoles

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

tournament_router = APIRouter(prefix="/api/v1/tournaments", tags=["Tournaments"])

@tournament_router.post("/", response_model=TournamentPublicComplete)
async def create_tournament(
    tournament: TournamentCreate,
    current_user: Annotated[UserSchema, Depends(userController.require_role("Admin"))], 
    db: Session = Depends(get_db)
):
    try:
        session_tournament = db.query(TournamentModel).filter(TournamentModel.name == tournament.name).first()

        if session_tournament:
            raise HTTPException(
                status_code=409,
                detail="The tournament with this name already exists in the system",
            ) 
        newT = TournamentModel(**tournament.model_dump(exclude={"creator"}))
        newT.creator_id = current_user.id
        db.add(newT)
        db.commit()
        db.refresh(newT)
        return newT
    except Exception as e:
        raise e

@tournament_router.post("/{tournament_id}/teams")
async def add_team_to_tournament(
    tournament_id: int,
    team_tournament: Team_in_T, 
    user: UserSchema = Depends(userController.require_role("Admin")), 
    db: Session = Depends(get_db)
):
    # Ensure tournament_id in path matches tournament_id in body
    if team_tournament.tournament_id != tournament_id:
        raise HTTPException(
            status_code=400,
            detail="Tournament ID in path does not match tournament ID in request body"
        )
        
    try:
        team_model = db.query(Team_Model).filter(Team_Model.id == team_tournament.team_id).first()
        print(team_model.name)
        tournament = db.query(TournamentModel).filter(TournamentModel.id == team_tournament.tournament_id).first()
        print(tournament.name)
    except Exception as e:
        raise HTTPException(status_code=404, detail="No se ha encontrado el equipo o el torneo a asignar")
        
    if team_model and tournament:    
        try:   
            tournament_team_model = TournamentTeam(
                tournament_id=team_tournament.tournament_id, 
                team_id=team_tournament.team_id
            )
            db.add(tournament_team_model)
            db.commit()
            db.refresh(tournament_team_model)
            response = {
                "Teams_in": tournament.teams_in_t, 
                "Tournament_id": tournament_team_model.tournament_id
            }
            return response
        except sqlalchemy.exc.IntegrityError as error:
            raise HTTPException(detail="Este equipo ya existe en este torneo", status_code=409)

@tournament_router.delete("/{tournament_id}")
async def delete_tournament(
    tournament_id: int,
    user: UserSchema = Depends(userController.require_role("Admin")), 
    db: Session = Depends(get_db)
):
    tournament = db.get_one(TournamentModel, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    db.delete(tournament)
    db.commit()
    return JSONResponse(content="Se ha eliminado el torneo con exito", status_code=200) 

@tournament_router.get("/", response_model=List[TournamentPublicComplete])
async def get_tournaments(
    user: UserSchema = Depends(userController.get_current_active_user), 
    db: Session = Depends(get_db)
):
    tournaments = db.query(TournamentModel).all()
    return tournaments

@tournament_router.patch("/{tournament_id}")
async def update_tournament(
    tournament_id: int,
    tournament: TournamentUpdate, 
    user: UserSchema = Depends(userController.require_role(DefaultRoles.ADMIN_ROL)), 
    db: Session = Depends(get_db)
):
    tnmt = db.get(TournamentModel, tournament_id)
    print(tnmt.name)
    if not tnmt:
        raise HTTPException(detail="Tournament not found", status_code=404)
        
    # Check if user is the creator of the tournament
    if tnmt.creator_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="Operation not permitted, Not enough permissions (only tournament's creators can update a tournament)"
        )
        
    t_dict = tournament.model_dump(exclude_unset=True)
    for k, v in t_dict.items():
        setattr(tnmt, k, v)
    db.commit()
    db.refresh(tnmt)
    return tnmt