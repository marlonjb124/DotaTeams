from typing import Annotated,List,Any
from uuid import UUID,uuid4
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
# from psycopg2.errors import UniqueViolation
# import sqlalchemy.exc
from fastapi.security import  OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
import jwt
from fastapi.responses import HTMLResponse,JSONResponse
from fastapi import APIRouter,Depends, HTTPException, status, Body
from datetime import  timedelta
from app.database.database import SessionLocal
from app.models.rol import Rol
from app.models.user import User as UserModel
from app.schemas.user_team import UserCreate
from app.schemas.rol import Rol as RolSchema,Rol_create as rol_create_schema
from app.schemas.user_team import UserReturn,TeamReturn,User
from app.controllers import userController 
from app.controllers import profileController
from app.models.user_rol import User_rol
from app.schemas import user_team as userSchema
from app.utils.connection import error_handler
from app.models.profile import Profile
from app.models.refresh_token import RefreshToken
from app.schemas.rol import DefaultRoles
from app.schemas.user_roles import User_rol as UserRolSchema


            

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

# @userRouter.post("/Create_rol",response_model=RolSchema)
# async def create_rol(rol:rol_create_schema,auth:userSchema=Depends(userController.require_role("Super_admin")),db:Session=Depends(get_db)):
#     rol_model = Rol(**rol.model_dump())
#     db.add(rol_model)
#     db.commit()
#     db.refresh(rol_model)
#     return rol_model


@userRouter.post("/", response_model=userSchema.User)
async def add_user(user: UserCreate, db: Session = Depends(get_db)):
    # Verificar si el usuario ya existe antes de iniciar la transacción
    if userController.get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=400,
            detail="El usuario con este correo electrónico ya existe"
        )
    
# Iniciar transacción

    # Crear objeto de usuario
    passw = user.password
    user_model = UserModel(**user.model_dump())
    user_model.password = userController.get_password_hash(passw)
    
    # Obtener el rol básico antes de realizar cambios
    # rol_1=db.query(Rol).filter(Rol.rol==DefaultRoles.BASIC_USER_ROL).first()
    # print(rol_1)
    rol_basic = db.query(Rol).filter_by(rol=DefaultRoles.BASIC_USER_ROL).first()
    print(rol_basic)
    if not rol_basic:
        raise HTTPException(
            status_code=500,
            detail="No se encontró el rol básico en la base de datos"
        )
    
    # Iniciar transacción explícita

        # Agregar usuario
    try:
        # Agregar usuario
        db.add(user_model)
        db.flush()  # Para obtener el ID
        
        # Crear perfil
        profile = Profile(user_id=user_model.id)
        db.add(profile)
        
        # Crear relación usuario-rol
        user_rol = User_rol(user_id=user_model.id, rol_id=rol_basic.id)
        db.add(user_rol)
        print(user_rol.__init__+123)       
        # Commit de la transacción
        db.commit()

        db.refresh(user_model)
        
        return user_model
        
    except Exception as e:
        # db.rollback()
        import logging
        logging.error(f"Error al crear usuario: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Huvo un error creando el usuario {e}"
        )
    
    
 


    
@userRouter.post("/token", response_model=userSchema.Token)
async def login(
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
    roles = [rol.rol for rol in user.rol] 
    access_token = userController.create_access_token(
        data={"sub": str(user.id),"roles":roles}, expires_delta=access_token_expires
    )
    print(access_token)
    ref_token = str(uuid4())
    print("ref_token", ref_token)
    refresh_token= userController.create_refresh_token(data={"sub": str(user.id),"token":ref_token})  
    print("refresh_token")  
    print(refresh_token)
    _ = userController.create_refresh_token_db(db,user.id,ref_token)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@userRouter.get("/me", response_model=userSchema.User)
def read_users_me(
    current_user: Annotated[userSchema.User, Depends(userController.get_current_active_user)]
    
):
   
    return current_user
@userRouter.post("/refresh", response_model=userSchema.Token)
async def refresh_token(
    refresh_token_in: userSchema.RefreshTokenRequest = Body(...),
    db: Session = Depends(get_db)
) -> Any:
    """
    Refresca un token de acceso usando un token de refresco.
    """
    try:
        # Decodificar el token de refresco
        payload = jwt.decode(
            refresh_token_in.refresh_token,
            userController.SECRET_KEY,
            algorithms=[userController.ALGORITHM]
        )
        print("Payload decodificado:", payload)  # Depuración
        
        # Verificar que el payload tenga la estructura esperada
        if "sub" not in payload or "type" not in payload or "token" not in payload:
            print("Payload incompleto:", payload)  # Depuración
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o malformado",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        token_data = userSchema.TokenPayload(**payload)
        
        # Verificar que sea un token de refresco
        if token_data.type != "refresh":
            print("Tipo de token incorrecto:", token_data.type)  # Depuración
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido (no es de refresco)",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verificar que el token no haya expirado
        if token_data.exp < datetime.now(timezone.utc):
            print("Token expirado:", token_data.exp)  # Depuración
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Obtener el token UUID del payload
        uuid_token = token_data.token
        print("UUID token:", uuid_token)  # Depuración
        raw_token = db.query(RefreshToken).filter(
            RefreshToken.user_id == token_data.sub,
            RefreshToken.revoked == False,
            RefreshToken.expires_at > datetime.now(timezone.utc)
        ).first()
        print("Token encontrado en DB:", raw_token)  # Depuración
        # Hashear el token UUID para compararlo con el almacenado
        hashed_token = userController.verify_password(uuid_token,raw_token.token)
        raw_token.user
        # Obtener el usuario asociado al token
        # user = db.query(UserModel).filter(UserModel.id == token_data.sub).first()
        if not raw_token.user or not raw_token.user.is_active:
            print("Usuario inactivo o no encontrado")  # Depuración
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuario inactivo o no encontrado",
            )
        
        # Generar nuevo token UUID
        new_uuid_token = str(uuid4())
        print("Nuevo UUID token:", new_uuid_token)  # Depuración
        
        # Crear nuevo token de acceso
        access_token_expires = timedelta(minutes=userController.ACCESS_TOKEN_EXPIRE_MINUTES)
        roles = [rol.rol for rol in user.rol]
        access_token = userController.create_access_token(
            data={"sub": str(user.id), "roles": roles},
            expires_delta=access_token_expires
        )
        
        # Crear nuevo token de refresco en la base de datos
        _ = userController.create_refresh_token_db(db, user.id, new_uuid_token)
        
        # Revocar el token anterior
        raw_token.revoked = True
        db.commit()
        
        # Crear nuevo token de refresco JWT
        refresh_token_expires = timedelta(days=userController.REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token = userController.create_refresh_token(
            data={"sub": str(user.id), "token": new_uuid_token},
            expires_delta=refresh_token_expires
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
        
    except (jwt.PyJWTError, ValueError) as e:
        print(f"Error en refresh token: {str(e)}")  # Depuración
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
@userRouter.post("/logout")
async def logout(
    refresh_token_in: userSchema.RefreshTokenRequest = Body(...),
    current_user: User = Depends(userController.get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Cierra la sesión del usuario revocando el token de refresco.
    """
    try:
        # Decodificar el token de refresco
        payload = jwt.decode(
            refresh_token_in.refresh_token,
            userController.SECRET_KEY,
            algorithms=userController.ALGORITHM
        )
        token_data = userSchema.TokenPayload(**payload)
        
        # Verificar que sea un token de refresco
        if token_data.type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido",
            )
        
        # Verificar que el token pertenezca al usuario actual
        if token_data.sub != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No autorizado",
            )
        
        # Revocar el token de refresco
        success = userController.revoke_refresh_token(db, token_data.sub)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token no encontrado o ya revocado",
            )
        
        return {"message": "Sesión cerrada correctamente"}
        
    except (jwt.PyJWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido",
        )
@userRouter.post("/Assign_role")
# @error_handler
async def assign_role(user_rol:UserRolSchema,current_user:userSchema.User =Depends(userController.require_role("Admin")),db:Session=Depends(get_db)):

    validate_rol = db.get(Rol,user_rol.rol_id)
    valdiate_user= db.get(UserModel,user_rol.user_id)

    if not validate_rol or not valdiate_user:
        raise HTTPException(status_code=404,detail="User or rol not found")
    
    try:
        rol_user = User_rol(**user_rol.model_dump())
        db.add(rol_user)
        rol = db.get(Rol,user_rol.rol_id)   
        db.commit()  
    except IntegrityError as e :
        # rol = db.get(Rol,user_rol.rol_id)   
        print(rol)   
    #     print(e.instance)
    #     print(e._sql_message)
    #     print(e.detail)
    #     # print(e.orig)
        raise HTTPException(detail=f"User already is {rol.rol}",status_code=400)
    # except Exception as e:
    #     raise HTTPException(detail=e,status_code=400)
    db.refresh(rol_user)

    return JSONResponse(content="Successfull",status_code=200)

@userRouter.get("/Roles/")
async def get_roles(db:Session=Depends(get_db),current_user:userSchema.User =Depends(userController.require_role(DefaultRoles.ADMIN_ROL))):
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