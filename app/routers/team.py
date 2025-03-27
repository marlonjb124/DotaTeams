from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter,Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from uuid import uuid4
import json
from datetime import datetime,timedelta
from typing import Annotated
# from typing import  ForwardRef
from app.database.database import SessionLocal
from app.models.user import User as UserModel
from app.schemas.user_team import TeamCreate, TeamUpdateSchema,TeamBase,User,Member,TeamReturn
# from app.schemas.tournament import Tournament
from app.models.team  import Team
from app.models.user_team import User_team
from app.controllers.userController import require_role,get_current_active_user
from app.schemas.invitacion import InvitacionCreate,InvitacionResponse
from app.models.invitacion import Invitacion as InvitacionModel
from app.controllers.teamController import add_user_to_team


# TeamReturn.model_rebuild()
teamRouter = APIRouter(prefix="/Teams",tags=["Teams"])
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
@teamRouter.post("/",response_model=TeamReturn)
async def create_team(team: TeamCreate ,user:User=Depends(require_role("Admin")),db: Session = Depends(get_db)):
    try:
        session_team = db.query(Team).filter(Team.name == team.name).first()

        # Player =UserModel(email="Daniel",password="1248")
        if session_team:
            raise HTTPException(
            status_code=400,
            detail="The team with this name already exists in the system",
        ) 
        teamModel =Team(**team.model_dump())
        teamModel.creator_id = user.id
        print(teamModel)
        db.add(teamModel)
        db.commit()
        db.refresh(teamModel)
        userteam= User_team(user_id = teamModel.creator_id,team_id = teamModel.id)
        print(userteam)
        db.add(userteam)
        db.commit()
        return teamModel
        # team_schema = TeamReturn(name=teamModel.name,creator=user,id=teamModel.id,members=[])
        # serializable = team_schema.model_dump()
        # print(serializable)
        # response = {"Team": serializable}
        # return JSONResponse(content=response,status_code=200)
    except Exception as e:
        raise e
# @teamRouter.post("/add_user_team",description="Agregar un miembro a un equipo",response_class= JSONResponse,)
# async def add_user_team(new_member:Member,db: Session = Depends(get_db)):
#         members = await add_user_to_team(new_member=new_member,db=db)
#         return JSONResponse(content= {"members":members["ids"]})
   
    
@teamRouter.delete("/{team_id}",description="Delete a team")
async def delete_team(team_id:int,db:Session = Depends(get_db),user:User =Depends(get_current_active_user)):

    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(detail="This team doesn't exist",status_code=404)
    if team.creator_id == user.id:
        db.delete(team)
        db.commit()
    else:  
        raise HTTPException(status_code=401)
          
    return JSONResponse(content="Deleted!",status_code=200)



@teamRouter.post("/Invite_user",description="Invite a user to the team",response_model=InvitacionResponse)
async def invite_user(invitacion:InvitacionCreate,db: Session =Depends(get_db),current_user= Annotated[User,Depends(require_role("Admin"))]):   
    token = str(uuid4())
    invitacionModel =InvitacionModel(token=token,invited_user_id=invitacion.invited_user_id,team_id=invitacion.team_id)
    db.add(invitacionModel)
    db.commit()
    db.refresh(invitacionModel)
    return invitacionModel



    # print(teamModel.creator.email)
@teamRouter.post("/Acept_invitacion/{token}",response_model=list[User])
async def Acept_invitacion(token:str,db:Session =Depends(get_db),current_user= Annotated[User,Depends(require_role("Admin"))]):
    invitacion = db.query(InvitacionModel).filter_by(token=token).first()
    now = datetime.now()
    token_time = invitacion.expToken + timedelta(minutes=10)
    bool_token = token_time > now
    # Si el token es válido y la invitación está pendiente
    if invitacion and invitacion.status == "pendiente" and bool_token:
        # Añade al usuario al equipo
        team = await add_user_to_team(new_member=Member(user_id=invitacion.invited_user_id,team_id=invitacion.team_id),db=db)
        # esta complejidad no es necesaria,solo fue para serializar y poder devovler una JsonResponse manualmente
        # dict=[]
        # for member in members:
        #     member_serialized = User(**member.__dict__)
        #     member_serialized = member_serialized.model_dump()
        #     dict.append(member_serialized)
        # members_serialized = [User(**member.__dict__)for member in members]
        # print(member_serialized)
        invitacion.status = "Aceptada"
        db.commit()
        # return JSONResponse(content={"Members":dict},status_code=201)
        return team.members
    else:
        raise HTTPException(status_code=404, detail="Invitación no válida o expirada")
    
@teamRouter.delete("/{id_team}/Member/{tarjet_member_id}")
async def drop_member(tarjet_member_id:int,id_team:int,user:Annotated[User, Depends(require_role("Admin"))],db:Session = Depends(get_db)):
    try:
        user_model:UserModel = db.query(UserModel).filter(UserModel.id == user.id).first()
        team_model:Team =db.query(Team).filter(Team.id == id_team).first()
        userteam= db.query(User_team).filter(User_team.user_id==tarjet_member_id).first()
        if not team_model:
            raise HTTPException(details="Team not found",status_code=404)
        if not userteam:
                raise HTTPException(details={"Info": f"User {tarjet_member_id} not found in team {id_team}"},status_code=404)
        if not team_model in user_model.teams_created:
            raise HTTPException(status_code=430,detail="Operation not permitted,Not enough permissions(only team's owners are able to delete a member)") 
        db.delete(userteam)
        db.commit()
        return JSONResponse(content={"Info": f"Se ha expulsado el usuario{tarjet_member_id}"},status_code=200)
        # for team in user_model.teams_created:
        #     if id_team == team.id:
        #         userteam= db.query(User_team).filter(User_team.user_id==tarjet_member_id).first()
        #         print(userteam)
        #         if not userteam:
        #             return JSONResponse(content={"Info": f"No se ha encontrado el usuario  {tarjet_member_id} en el equipo  {id_team}"})
        #         db.delete(userteam)
        #         db.commit()
        #         return JSONResponse(content={"Info": f"Se ha expulsado el usuario{tarjet_member_id}"})
        # raise HTTPException(status_code=430,detail="Operation not permitted,Not enough permissions(should be a team manager)")   
    except Exception as e:
        raise e
@teamRouter.get("/",response_model=list[TeamReturn])
async def get_teams(user:User=Depends(get_current_active_user),db:Session=Depends(get_db)):
    teams = db.query(Team).all()
    print(teams)
    # team_schema = [
    #     {
    #         "Team": TeamReturn(**team.__dict__).model_dump(),
    #         "Tournaments_in": jsonable_encoder(team.tournaments)
    #     }
    #     for team in teams
    # ]
    # return JSONResponse(content={"Teams":team_schema},status_code=200)
    return teams

    
@teamRouter.patch("/")
async def update_team(teamSchema:TeamUpdateSchema,user:User=Depends(require_role("Admin")),db:Session =Depends(get_db)):

    team_to_update=db.get(Team,teamSchema.id)
    # tournaments = getattr(team_to_update,"tournaments")
    # print('23232',tournaments)
    if not team_to_update:
        raise HTTPException(detail="No se ha encontrado el equipo a actualizar",status_code=404)
    team_data=teamSchema.model_dump(exclude_unset=True)
    for key, value in team_data.items():
        setattr(team_to_update, key, value)
        
    db.commit()
    db.refresh(team_to_update)
    # dicted= team_to_update.__dict__
    response_team = TeamReturn.model_validate(team_to_update)
    # response_team = TeamReturn(**team_to_update.__dict__)
    # print(dicted)
    print(response_team)
    return JSONResponse(content=response_team.model_dump(),status_code=200)
    
    
    
    
    
    # userteam= User_team(user_id= user.id,team_id=id_team).first()
    # db.delete(userteam)
    # db.commit()
    # return JSONResponse(content={"Info": f"Se ha expulsado el usuario{tarjet_member_id}"})
    # passw = user.password
    # UserModel = UserModel(**user.model_dump())
    # UserModel.password= userController.get_password_hash(passw)
    # # print(UserModel.password)
    
    # db.add(UserModel)
    # db.commit()
    # print(UserModel.id)
    # profile = profileController.createPerfil(UserModel.id)
    
    # db.refresh(UserModel)
    
    # db.add(profile)
    # db.commit()
    # db.refresh(profile)
    # return userSchema(**UserModel.__dict__)
    