from fastapi.responses import HTMLResponse
from fastapi import APIRouter,Depends, HTTPException, status
from datetime import datetime, timedelta, timezone
from database.database import SessionLocal
from sqlalchemy.orm import Session
from models.user import User as UserModel
from typing import Annotated
from schemas.user import UserCreate
from fastapi.security import  OAuth2PasswordRequestForm
from controllers import userController 
from controllers import profileController

from schemas import user as userSchema


            

userRouter = APIRouter(prefix="/User",tags=["usuarios"])
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@userRouter.get("")
def home()->HTMLResponse:
    html = """
    <html>
        <head>
            <title>Home</title>
        </head>
        <body>
            <h1>ElcesaLesabe</h1>
        </body>
    </html>
    """

    return HTMLResponse(content=html, status_code=200)




@userRouter.post("/addUser")
async def add_user(user: UserCreate, db: Session = Depends(get_db)):
    passw = user.password
    userModel = UserModel(**user.model_dump())
    userModel.password= userController.get_password_hash(passw)
    # print(userModel.password)
    
    db.add(userModel)
    db.commit()
    print(userModel.id)
    profile = profileController.createPerfil(userModel.id)
    
    db.refresh(userModel)
    
    db.add(profile)
    db.commit()
    db.refresh(profile)
    # return UserReturn(**userModel.__dict__)
    
@userRouter.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm,Depends()],db: Session = Depends(get_db)
) -> userSchema.Token:
    # user = db.query(UserModel).filter(UserModel.email == form_data.username).first()
    user = userController.authenticate_user( form_data.username, form_data.password,db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=userController.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = userController.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return userSchema.Token(access_token=access_token, token_type="bearer")


@userRouter.get("/me", response_model=userSchema.User)
def read_users_me(
    current_user: Annotated[userSchema.User, Depends(userController.get_current_active_user)]
    
):
   
    return current_user


# @userRouter.get("/users/me/items/")
# async def read_own_items(
#     current_user: Annotated[userSchema.User, Depends(get_current_active_user)]
# ):
#     return [{"item_id": "Foo", "owner": current_user.email}]
# # profile = db.query(profileModel).filter(profileModel.user_id == user_id).update(**profile.model_dump())