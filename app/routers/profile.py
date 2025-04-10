
from typing import Annotated
from fastapi import APIRouter, HTTPException,Depends
from app.database.database import SessionLocal, engine
from app.schemas.profile import Profile,ProfileReturn
from app.models.profile import Profile as profileModel
from sqlalchemy.orm import Session
from app.models.user import User as UserModel
from app.schemas.user_team import User as UserSchema
from app.controllers import userController

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

profilerouter = APIRouter(prefix="/Profile",tags=["Profiles"])



# @profilerouter.get("/GetBodyFat")
# async def getBF(user:Annotated[UserSchema,Depends(userController.get_current_active_user)],db: Session = Depends(get_db)):
#     try:

#         user = UserModel(**user.model_dump())       
#         userModel =db.query(UserModel).filter(UserModel.id == user.id).first()
        
#         print(userModel.profile.age)
        
#         if userModel.profile is None:
#             raise HTTPException(status_code=400, detail="User profile does not exist")
#         edad= userModel.profile.age
#         Imc= userModel.profile.icm
#         sexo = userModel.profile.gender
#         Pmc =  (1.20*Imc) 
#         return Pmc

#     except Exception as e:
#         # raise HTTPException(status_code=500, detail=str(e))
#         raise e


@profilerouter.put("/updateProfile")
async def updateprofile(profile: Profile,user:Annotated[UserSchema,Depends(userController.get_current_active_user)], db: Session = Depends(get_db)):
    # userdb = UserModel(**user.model_dump(exclude="rol"))
    profileToUpdt = db.query(profileModel).filter(profileModel.user_id == user.id).first()
    
    profilenew = profile.model_dump()
    for key, value in profilenew.items():
        setattr(profileToUpdt, key, value) 
    # db.add(profileToUpdt)
    db.commit()
    db.refresh(profileToUpdt)
    return ProfileReturn(**profileToUpdt.__dict__)
    