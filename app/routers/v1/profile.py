from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from app.database.database import SessionLocal, engine
from app.schemas.profile import Profile, ProfileReturn
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

profile_router = APIRouter(prefix="/api/v1/profiles", tags=["Profiles"])

@profile_router.put("/me")
async def update_profile(
    profile: Profile,
    user: Annotated[UserSchema, Depends(userController.get_current_active_user)], 
    db: Session = Depends(get_db)
):
    profileToUpdt = db.query(profileModel).filter(profileModel.user_id == user.id).first()
    
    if not profileToUpdt:
        # Create profile if it doesn't exist
        profileToUpdt = profileModel(user_id=user.id, **profile.model_dump())
        db.add(profileToUpdt)
    else:
        # Update existing profile
        profilenew = profile.model_dump()
        for key, value in profilenew.items():
            setattr(profileToUpdt, key, value) 
            
    db.commit()
    db.refresh(profileToUpdt)
    return ProfileReturn(**profileToUpdt.__dict__)