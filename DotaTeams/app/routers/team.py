from fastapi.responses import JSONResponse
from fastapi import APIRouter,Depends, HTTPException, status
from database.database import SessionLocal
from sqlalchemy.orm import Session
from models.user import User as UserModel
from schemas.team import TeamCreate
from models.team  import Team
from models.user_team import User_team
from schemas.user_team import Member

teamRouter = APIRouter(prefix="/Team",tags=["Teams"])
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
@teamRouter.post("/create_team")
async def create_team(team: TeamCreate, db: Session = Depends(get_db)):
    try:
        Player =UserModel(email="Daniel",password="1248")
        teamModel = Team(**team.model_dump())
        print(teamModel)
        db.add(teamModel)
        db.commit()
        db.refresh(teamModel)
        userteam= User_team(user_id = team.creator_id,team_id = teamModel.id)
        print(userteam)
        db.add(userteam)
        db.commit()
        usuarios = teamModel.members
        for usuario in usuarios:
            print(usuario.email)
        return JSONResponse(content= teamModel.name,status_code=200)
    except Exception as e:
        raise e
@teamRouter.post("/add_user_team",description="Agregar un miembro a un equipo",response_class= JSONResponse,)
async def add_user_team(new_member:Member,db: Session = Depends(get_db)):
    try:
    
        userteam= User_team(user_id= new_member.user_id,team_id=new_member.team_id)
        db.add(userteam)
        db.commit()
        Kevin = db.query(UserModel).filter(UserModel.email=="kevin").first()
        print(Kevin.teams_created)
        for i in range(len(Kevin.teams)):           
            print(Kevin.teams[i].id)

        # relaciones = db.query(User_team).order_by(User_team.team_id).all()
        miembros = db.query(User_team).filter(User_team.team_id==userteam.team_id).all()
        members={"ids":[]}
        for i in range(len(miembros)):
            members["ids"].append(miembros[i].user_id)          
        # serializable = json.loads(json.dumps(members["ids"],default=str))
        return JSONResponse(content= {"members":members["ids"]})
    except Exception as e:
        raise e
    
    
    # print(teamModel.creator.email)

    # passw = user.password
    # userModel = UserModel(**user.model_dump())
    # userModel.password= userController.get_password_hash(passw)
    # # print(userModel.password)
    
    # db.add(userModel)
    # db.commit()
    # print(userModel.id)
    # profile = profileController.createPerfil(userModel.id)
    
    # db.refresh(userModel)
    
    # db.add(profile)
    # db.commit()
    # db.refresh(profile)
    # return userSchema(**userModel.__dict__)
    