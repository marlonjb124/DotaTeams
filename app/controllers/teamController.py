from ..schemas.user_team import Member
from ..models.user_team import User_team
from ..models import team,user as userModel
from ..database.database import SessionLocal
from sqlalchemy.orm import Session
from fastapi import Depends,HTTPException
from typing import Annotated
from ..schemas import user_team
from ..controllers import userController
# from fastapi.responses import JSONResponse
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
async def add_user_to_team(new_member:Member,db: Session = Depends(get_db)):
    try:
    
        userteam= User_team(user_id= new_member.user_id,team_id=new_member.team_id)
        db.add(userteam)
        db.commit()
        team_search = db.query(team.Team).filter(team.Team.id==userteam.team_id).first()
        print(team_search.members)
        # Kevin = db.query(UserModel).filter(UserModel.email=="kevin").first()
        # print(Kevin.teams_created)
        # for i in range(len(Kevin.teams)):           
        #     print(Kevin.teams[i].id)

        # relaciones = db.query(User_team).order_by(User_team.team_id).all()

        # miembros = db.query(User_team).filter(User_team.team_id==userteam.team_id).all()
        # members={"ids":[]}
        # for i in range(len(miembros)):
        #     members["ids"].append(miembros[i].user_id)          
        # serializable = json.loads(json.dumps(members["ids"],default=str))
        # return JSONResponse(content= {"members":members["ids"]})
        return team_search.members
    except Exception as e:
        raise e
    current_user: Annotated[UserSchema, Depends(userController.require_role("Admin"))]
# async def drop_member(tarjet_member_id:str,id_team:str,user:Annotated[user.User, Depends(userController.get_current_active_user)],db:Session = Depends(get_db)):
#     user_model:userModel.User = db.query(userModel).filter(userModel.User.id == user.id).first()
#     print(user_model.teams_created)
#     if id_team not in user_model.teams_created:
#         raise HTTPException(status_code=430,detail="Operation not permitted,Not enough permissions(should be a team manager)")
    
#     userteam= User_team(user_id= user.id,team_id=id_team).first()
#     db.delete(userteam)
#     db.commit()