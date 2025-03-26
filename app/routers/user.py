from typing import Annotated,List
from sqlalchemy.exc import IntegrityError
# from psycopg2.errors import UniqueViolation
# import sqlalchemy.exc
from fastapi.responses import HTMLResponse,JSONResponse
from fastapi import APIRouter,Depends, HTTPException, status
from datetime import  timedelta
from app.database.database import SessionLocal
from sqlalchemy.orm import Session
from app.models.rol import Rol
from app.models.user import User as UserModel
from app.schemas.user_roles import User_rol as User_rol_schema
from app.schemas.user_team import UserCreate
from app.schemas.rol import Rol as RolSchema,Rol_create as rol_create_schema
from app.schemas.user_team import UserReturn,TeamReturn,User
from fastapi.security import  OAuth2PasswordRequestForm
from app.controllers import userController 
from app.controllers import profileController
from app.models.user_rol import User_rol
from app.schemas import user_team as userSchema
from app.utils.connection import error_handler



            

userRouter = APIRouter(prefix="/Users",tags=["Users"])
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

@userRouter.post("/Create_rol",response_model=RolSchema)
async def create_rol(rol:rol_create_schema,auth:userSchema=Depends(userController.require_role("just to know Super_admin")),db:Session=Depends(get_db)):
    rol_model = Rol(**rol.model_dump())
    db.add(rol_model)
    db.commit()
    db.refresh(rol_model)
    return rol_model


@userRouter.post("/",response_model=userSchema.User)
async def add_user(user: UserCreate, db: Session = Depends(get_db),auth:userSchema=Depends(userController.require_role("Admin"))):
    passw = user.password
    userModel = UserModel(**user.model_dump(exclude={"rol"}))
    userModel.password= userController.get_password_hash(passw)
    # print(userModel.password)
    db.add(userModel)
    db.commit()
    profile = profileController.createPerfil(userModel.id)
    db.refresh(userModel)
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
    return userModel
    
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
# @error_handler
async def assign_role(user_rol:User_rol_schema,current_user:userSchema.User =Depends(userController.require_role("Admin")),db:Session=Depends(get_db)):
    print("asdas")
    validate_rol = db.get(Rol,user_rol.rol_id)
    valdiate_user= db.get(UserModel,user_rol.user_id)
    #  db.query(User_rol).filter(User_rol.rol_id==user_rol.rol_id,User_rol.user_id==user_rol.user_id).first()
    print("rol")
    # print(validate_rol)
    if not validate_rol or not valdiate_user:
        raise HTTPException(status_code=404,detail="User or rol not found")
    
    try:
        rol_user = User_rol(**user_rol.model_dump())
        print(rol_user)
        db.add(rol_user)
        rol = db.get(Rol,user_rol.rol_id)   
        print(rol)
        db.commit()  
    except IntegrityError as e :
        rol = db.get(Rol,user_rol.rol_id)   
        print(rol)   
    #     print(e.instance)
    #     print(e._sql_message)
    #     print(e.detail)
    #     # print(e.orig)
        raise HTTPException(detail=f"El usuario ya posee el rol de {rol.rol}",status_code=400)
    # except Exception as e:
    #     raise HTTPException(detail=e,status_code=400)
    db.refresh(rol_user)
    print(rol_user)
    return JSONResponse(content="Successfull",status_code=200)

@userRouter.get("/Roles/")
async def get_roles(db:Session=Depends(get_db)):
    roles=db.query(Rol).all()
    return roles

@userRouter.get("/{user_id}", response_model=UserReturn) 
async def find_user(user_id: int, db: Session = Depends(get_db),user:User =Depends(userController.get_current_active_user)):
    db_user = db.get(UserModel, user_id)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Serializar equipos manualmente
    # teams_data = [Team.model_validate(team.__dict__) for team in db_user.teams]
    # teams_created_data = [Team.model_validate(team.__dict__) for team in db_user.teams_created]

    # # Crear el diccionario con datos serializados
    # user_dict = db_user.__dict__.copy()
    # user_dict["teams"] = teams_data
    # user_dict["teams_created"] = teams_created_data

    # Validar con Pydantic
    # data_user = UserReturn.model_validate(user_dict)

    # return data_user
    return db_user
@userRouter.get("/", response_model=List[UserReturn]) 
async def get_users( db: Session = Depends(get_db),user:User =Depends(userController.get_current_active_user)):
    user_list = db.query(UserModel).all()
    return user_list

#     return [{"item_id": "Foo", "owner": current_user.email}]
# # profile = db.query(profileModel).filter(profileModel.user_id == user_id).update(**profile.model_dump())