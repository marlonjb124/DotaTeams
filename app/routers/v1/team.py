from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from uuid import uuid4
import json
from datetime import datetime, timedelta
from typing import Annotated, List
from app.database.database import SessionLocal
from app.models.user import User as UserModel
from app.models.user_rol import User_rol
from app.schemas.user_team import TeamCreate, TeamUpdateSchema, TeamBase, User, Member, TeamReturn
from app.models.rol import Rol
from app.models.team import Team
from app.models.user_team import User_team
from app.controllers.userController import require_role, get_current_active_user, assign_role
from app.schemas.invitacion import InvitacionCreate, InvitacionResponse
from app.schemas.rol import DefaultRoles
from app.models.invitacion import Invitacion as InvitacionModel
from app.schemas.user_roles import User_rol
from app.controllers.teamController import add_user_to_team

teamRouter = APIRouter(prefix="/api/v1/teams", tags=["Teams"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@teamRouter.post("/", response_model=TeamReturn)
async def create_team(
    team: TeamCreate, 
    user: User = Depends(require_role(DefaultRoles.BASIC_USER_ROL)), 
    db: Session = Depends(get_db)
):
    try:
        session_team = db.query(Team).filter(Team.name == team.name).first()

        if session_team:
            raise HTTPException(
                status_code=409,
                detail="A team with this name already exists in the system",
            ) 
        teamModel = Team(**team.model_dump())
        teamModel.creator_id = user.id
        print(teamModel)
        db.add(teamModel)
        db.commit()
        db.refresh(teamModel)
        userteam = User_team(user_id=teamModel.creator_id, team_id=teamModel.id)
        print(userteam)
        db.add(userteam)
        db.commit()
        team_gestor = db.query(Rol).filter_by(rol=DefaultRoles.TEAM_GESTOR_ROL).first()
        user_rol_schema = User_rol(rol_id=team_gestor.id, user_id=user.id)
        _ = assign_role(user_rol_schema, db=db)
        
        return teamModel
    except Exception as e:
        raise e

@teamRouter.delete("/{team_id}")
async def delete_team(
    team_id: int, 
    db: Session = Depends(get_db), 
    user: User = Depends(require_role(DefaultRoles.TEAM_GESTOR_ROL))
):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(detail="This team doesn't exist", status_code=404)
    if team.creator_id == user.id:
        db.delete(team)
        db.commit()
    else:  
        raise HTTPException(status_code=403)
          
    return JSONResponse(content="Deleted!", status_code=200)

@teamRouter.post("/{team_id}/invitations", response_model=InvitacionResponse)
async def invite_user_to_team(
    team_id: int,
    invitacion: InvitacionCreate, 
    db: Session = Depends(get_db), 
    _ = Annotated[User, Depends(require_role(DefaultRoles.TEAM_GESTOR_ROL))]
):   
    # Ensure the team_id in the path matches the team_id in the body
    if invitacion.team_id != team_id:
        raise HTTPException(
            status_code=400,
            detail="Team ID in path does not match team ID in request body"
        )
        
    token = str(uuid4())
    invitacionModel = InvitacionModel(
        token=token, 
        invited_user_id=invitacion.invited_user_id, 
        team_id=invitacion.team_id
    )
    db.add(invitacionModel)
    db.commit()
    db.refresh(invitacionModel)
    return invitacionModel

@teamRouter.post("/invitations/{token}/accept")
async def accept_team_invitation(
    token: str, 
    db: Session = Depends(get_db), 
    _ = Annotated[User, Depends(require_role(DefaultRoles.BASIC_USER_ROL))]
):
    invitacion = db.query(InvitacionModel).filter_by(token=token).first()
    now = datetime.now()
    token_time = invitacion.expToken + timedelta(minutes=10)
    bool_token = token_time > now
    
    # Si el token es válido y la invitación está pendiente
    if invitacion and invitacion.status == "pendiente" and bool_token:
        # Añade al usuario al equipo
        team = await add_user_to_team(
            new_member=Member(
                user_id=invitacion.invited_user_id, 
                team_id=invitacion.team_id
            ), 
            db=db
        )
        invitacion.status = "Aceptada"
        db.commit()
        return team.members
    else:
        raise HTTPException(status_code=404, detail="Invitación no válida o expirada")

@teamRouter.delete("/{team_id}/members/{member_id}")
async def remove_member_from_team(
    team_id: int,
    member_id: int,
    user: Annotated[User, Depends(require_role(DefaultRoles.TEAM_GESTOR_ROL))], 
    db: Session = Depends(get_db)
):
    try:
        user_model: UserModel = db.query(UserModel).filter(UserModel.id == user.id).first()
        team_model: Team = db.query(Team).filter(Team.id == team_id).first()
        userteam = db.query(User_team).filter(User_team.user_id == member_id).first()
        
        if not team_model:
            raise HTTPException(details="Team not found", status_code=404)
        if not userteam:
            raise HTTPException(
                details={"Info": f"User {member_id} not found in team {team_id}"}, 
                status_code=404
            )
        if not team_model in user_model.teams_created:
            raise HTTPException(
                status_code=403,
                detail="Operation not permitted, Not enough permissions (only team's owners are able to delete a member)"
            ) 
            
        db.delete(userteam)
        db.commit()
        return JSONResponse(
            content={"Info": f"Se ha expulsado el usuario {member_id}"}, 
            status_code=200
        )
    except Exception as e:
        raise e

@teamRouter.get("/", response_model=List[TeamReturn])
async def get_teams(db: Session = Depends(get_db)):
    teams = db.query(Team).all()
    print(teams)
    return teams

@teamRouter.patch("/{team_id}")
async def update_team(
    team_id: int,
    teamSchema: TeamUpdateSchema, 
    user: User = Depends(require_role(DefaultRoles.TEAM_GESTOR_ROL)), 
    db: Session = Depends(get_db)
):
    team_to_update = db.get(Team, team_id)
    
    # Check if team exists
    if not team_to_update:
        raise HTTPException(detail="No se ha encontrado el equipo a actualizar", status_code=404)
        
    # Check if user is the creator of the team
    if team_to_update.creator_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="Operation not permitted, Not enough permissions (only team's owners can update a team)"
        )
        
    team_data = teamSchema.model_dump(exclude_unset=True)
    for key, value in team_data.items():
        setattr(team_to_update, key, value)
        
    db.commit()
    db.refresh(team_to_update)
    response_team = TeamReturn.model_validate(team_to_update)
    return JSONResponse(content=response_team.model_dump(), status_code=200)