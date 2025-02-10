from typing import Annotated
from sqlalchemy.exc import IntegrityError
# from psycopg2.errors import UniqueViolation
# import sqlalchemy.exc
from fastapi.responses import HTMLResponse,JSONResponse
from fastapi import APIRouter,Depends, HTTPException, status
from datetime import  timedelta
from ..database.database import SessionLocal
from sqlalchemy.orm import Session
from ..models.rol import Rol
from ..models.user import User as UserModel
from ..models.user_rol import User_rol
from ..schemas.user_roles import User_rol as User_rol_schema
from ..schemas.user_team import UserCreate
from ..schemas.rol import Rol_create as rol_create_schema
from ..schemas.user_team import UserReturn
from ..schemas.user_team import Team
from fastapi.security import  OAuth2PasswordRequestForm
from ..controllers import userController 
from ..controllers import profileController
from ..models.user_rol import User_rol
from ..schemas import user_team as userSchema


            

userRouter = APIRouter(prefix="/User",tags=["Users"])
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

@userRouter.post("/Create_rol")
async def create_rol(rol:rol_create_schema,auth:userSchema=Depends(userController.require_role("just to know Super_admin")),db:Session=Depends(get_db)):
    rol_model = Rol(**rol.model_dump())
    db.add(rol_model)
    db.commit()
    db.refresh(rol_model)
    return rol_model


@userRouter.post("/Add_user")
async def add_user(user: UserCreate, db: Session = Depends(get_db),auth:userSchema=Depends(userController.require_role("Admin"))):
    print("entre")
    passw = user.password
   
    userModel = UserModel(**user.model_dump(exclude={"rol"}))
    userModel.password= userController.get_password_hash(passw)
    # print(userModel.password)
    db.add(userModel)
    db.commit()
    profile = profileController.createPerfil(userModel.id)
    db.refresh(userModel)
    print(userModel.id)
    db.add(profile)
    db.commit()
    
    rol_guest= db.query(Rol).filter(Rol.rol == user.rol[0].rol).first()
    print(rol_guest.id)
    print("id_rol_guest")
    user_rol = User_rol(user_id=userModel.id,rol_id=rol_guest.id)
    db.add(user_rol)
    db.commit()
    db.refresh(userModel)
    # db.refresh(profile)
    # return userSchema.User(id=userModel.id ,is_active=userModel.is_active ,email=userModel.email)
    return userSchema.User(**userModel.__dict__)
    
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
@userRouter.post("/Assign_role")
async def assign_role(user_rol:User_rol_schema,current_user:userSchema.User =Depends(userController.require_role("Admin")),db:Session=Depends(get_db)):
    validate_rol = db.query(Rol).get(user_rol.rol_id)
   
    if not validate_rol:
        raise HTTPException(status_code=404,detail="rol_not_found")
    try:
        rol_user = User_rol(**user_rol.model_dump())
        db.add(rol_user)
        rol = db.get(Rol,user_rol.rol_id)   
        name =rol.rol
        db.commit()  
    except IntegrityError as e :   
        print(e.instance)
        print(e._sql_message)
        print(e.detail)
        raise HTTPException(detail=f"El usuario ya posee el rol de {name}",status_code=400)
    # except Exception as e:
    #     raise HTTPException(detail=e,status_code=400)
    db.refresh(rol_user)
    print(rol_user)
    return JSONResponse(content="Successfull",status_code=200)

@userRouter.get("/Roles")
async def get_roles(db:Session=Depends(get_db)):
    roles=db.query(Rol).all()
    return roles

@userRouter.get("/{user_id}") 
async def find_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.get(UserModel, user_id)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Serializar equipos manualmente
    teams_data = [Team.model_validate(team.__dict__) for team in db_user.teams]
    teams_created_data = [Team.model_validate(team.__dict__) for team in db_user.teams_created]

    # Crear el diccionario con datos serializados
    user_dict = db_user.__dict__.copy()
    user_dict["teams"] = teams_data
    user_dict["teams_created"] = teams_created_data

    # Validar con Pydantic
    data_user = UserReturn.model_validate(user_dict)

    return data_user


#     return [{"item_id": "Foo", "owner": current_user.email}]
# # profile = db.query(profileModel).filter(profileModel.user_id == user_id).update(**profile.model_dump())