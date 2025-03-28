
import sqlalchemy
from typing import List
from typing import Annotated
from fastapi import APIRouter, HTTPException,Depends
from fastapi.responses import JSONResponse,Response
import sqlalchemy.exc
from app.database.database import SessionLocal
from sqlalchemy.orm import Session
from app.models.user import User as UserModel
from app.schemas.user_team import User as UserSchema
from app.controllers import userController
from app.models.tournaments import Tournament as TournamentModel
from app.models.tournaments_teams import TournamentTeam
from app.models.team import Team as Team_Model
from app.schemas.tournament import TournamentCreate,Tournament, TournamentPublicComplete,TournamentUpdate
from app.schemas.user_team import Team,TeamBase 
from app.schemas.rol import DefaultRoles
# from app.schemas.user_team import User
from app.schemas.team_tournament import Team_in_T
# Tournament.model_rebuild()
# TournamentPublicComplete.model_rebuild()
# TournamentPublicComplete.model_rebuild()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

tournament_router = APIRouter(prefix="/Tournaments",tags=["Tournaments"])
@tournament_router.post("/CreateTournament",response_model=TournamentPublicComplete)
async def create_tournament(current_user: Annotated[UserSchema, Depends(userController.require_role("Admin"))],tournament : TournamentCreate,db:Session = Depends(get_db)):
    # userM =UserModel(**current_user.model_dump(exclude="rol"))
    try:
        session_tournament = db.query(TournamentModel).filter(TournamentModel.name == tournament.name).first()

        # Player =UserModel(email="Daniel",password="1248")
        if session_tournament:
            raise HTTPException(
            status_code=400,
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
    # schema = Tournament(name=newT.name,id=newT.id,creator=current_user,teams_in_t=[])
    
@tournament_router.post("/add_Team_Tournament/{tournament_id}",response_description="Team_in_T")
async def add_team_tournament(team_tournament:Team_in_T,user:UserSchema = Depends(userController.require_role("Admin")),db:Session=Depends(get_db)):
    try:
        team_model= db.query(Team_Model).filter(Team_Model.id == team_tournament.team_id).first()
        print(team_model.name)
        tournament = db.query(TournamentModel).filter(TournamentModel.id == team_tournament.tournament_id).first()
        print(tournament.name)
    except Exception as e:
        raise HTTPException(status_code=404,detail="No se ha encontrado el equipo o el torneo a asignar")
    if team_model and tournament:    
        try:   
            tournament_team_model = TournamentTeam(tournament_id=team_tournament.tournament_id,team_id =team_tournament.team_id)
            db.add(tournament_team_model)
            db.commit()
            db.refresh(tournament_team_model)
            response = {"Teams_in":tournament.teams_in_t,"Tournament_id":tournament_team_model.tournament_id}
            
            return response
        except sqlalchemy.exc.IntegrityError as error:
            raise HTTPException(detail= "Este equipo ya existe en este torneo",status_code=400)

@tournament_router.delete("/")
async def delete_tournament(tournament_id:int,user:UserSchema=Depends(userController.require_role("Admin")),db:Session=Depends(get_db)):
    tournament = db.get_one(TournamentModel,tournament_id)
    db.delete(tournament)
    db.commit()
    return JSONResponse(content="Se ha eliminado el torneo con exito",status_code=203) 

@tournament_router.get("/",response_model=List[TournamentPublicComplete])
async def get_tournaments(user:UserSchema=Depends(userController.get_current_active_user),db:Session=Depends(get_db)):
    tournaments = db.query(TournamentModel).all()
    # list:List[TournamentModel] = []
    # # dict = {}
    # for to in tournaments:
    #     print(type(to))
    #     print(to.__dict__)
    #     # print(to.teams_in_t)
    #     # dict[""]
    #     list.append(to.__dict__)
    # return JSONResponse(content=list,status_code=200)
    return tournaments
@tournament_router.patch("/",response_model=Tournament)
async def update_tournament(tournament:TournamentUpdate,user:UserSchema=Depends(userController.require_role(DefaultRoles.ADMIN_ROL)),db:Session=Depends(get_db)):
    tnmt=db.get(TournamentModel,tournament.id)
    print(tnmt.name)
    if not tnmt:
        raise HTTPException(detail="Tournament not found",status_code=404)
    t_dict = tournament.model_dump(exclude_unset=True)
    for k,v in t_dict.items():
        setattr(tnmt,k,v)
    db.commit()
    db.refresh(tnmt)
    return tnmt
    # response_tnmt = Tournament.model_validate(tnmt)
    # print(response_tnmt)
    # return JSONResponse(content=response_tnmt.model_dump(),status_code=200)
