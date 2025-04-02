
from fastapi import APIRouter,Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from typing import Annotated,Dict,Any
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session, selectinload
from uuid import UUID, uuid4
from app.models.refresh_token import RefreshToken
from app.models.user import User as UserModel
from app.models.rol import Rol as Rol_model
from app.schemas.rol import Rol as Rol_schema
from app.database.database import SessionLocal
from app.schemas import user_team as userSchema
from app.schemas.rol import DefaultRoles
from app.schemas.user_roles import User_rol as User_rol_schema
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/Users/token")
SECRET_KEY = "09d25e095faa6ca2556c818167b7a9563b93f7099f6f0f4caa6cf63b88e8d3e8"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS= 5
def create_roles(rol:Rol_schema,db:Session=Depends(get_db)):
    model = Rol_model(**rol.model_dump())
    print(model)
    db.add(model)
    db.commit()
def clean_roles(db:Session=Depends(get_db)):
    roles=db.query(Rol_model).delete(synchronize_session=False)
    db.commit()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)

def get_user_by_id(db: Session, id: str):
    return db.get(UserModel, id)
def get_user_by_email(db: Session, email: str):
    return db.query(UserModel).filter(UserModel.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(UserModel).offset(skip).limit(limit).all()

def get_user(db: Session, email:str):
   
    current_user = db.query(UserModel).filter(UserModel.email == email).first()
    # print("current")
    # dict_user=current_user.__dict__
    # to_schema={}
    # for k,v in dict_user.items() :
    #     if k!="rol":
    #         to_schema[f"{k}"]= v
    # for rol in current_user.rol:
    #     rol_dict = rol.__dict__
    #     print(current_user.__dict__)
    #     print(rol_dict)
    #     print("sad")
    
    userSchemaDB = userSchema.User(**current_user.__dict__)
    print(userSchemaDB)
    # print(userSchemaDB.rol)

    #     print(rol.rol)
    return userSchemaDB
 


def authenticate_user( email: str, password: str,db: Session = Depends(get_db)):
    user =  db.query(UserModel).filter(UserModel.email == email).first()

    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    # roles=[rol.rol for rol in user.rol]
    # print(roles)
    # if DefaultRoles. not in roles:
    #     user.rol.append()
    #     db.commit()
    #     db.refresh(User)
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
        print(expire)
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        print(expire)
    to_encode.update({"exp": expire, "type": "access"})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any], expires_delta: timedelta|None=None) -> str:
    """Crea un token JWT de refresco."""
    to_encode = data.copy()
    print("to_encode")
    print(to_encode)
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY,ALGORITHM)
    return encoded_jwt
def create_refresh_token_db(db: Session, user_id: int, token_value: str) -> RefreshToken:
        """Crea un token de refresco en la base de datos."""
        
        hashed_token= get_password_hash(token_value)
        expires_at = datetime.now(timezone.utc) + timedelta(days=5)
        
        refresh_token = RefreshToken(
            user_id=user_id,
            token=hashed_token,
            expires_at=expires_at,
            revoked=False,
        )
        db.add(refresh_token)
        db.commit()
        db.refresh(refresh_token)
        return refresh_token
    
def get_refresh_token(db: Session, user_id:int) -> RefreshToken|None:
    """Obtiene un token de refresco por su valor."""
    # print(f"Buscando token: {token}")  # Depuración
    
    # Primero buscar sin restricciones para depuración
    all_tokens = db.query(RefreshToken).all()
    print(f"Total tokens en DB: {len(all_tokens)}")  # Depuración
    
    # Buscar el token específico
    result = db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id== user_id,
            RefreshToken.revoked == False,
            RefreshToken.expires_at > datetime.now(timezone.utc)
        ).options(selectinload(RefreshToken.user))
    )
    token_record = result.scalars().first()
    
    print(f"Token encontrado: {token_record is not None}")  # Depuración
    return token_record



def revoke_refresh_token(db:Session, token: str) -> bool:
    """Revoca un token de refresco."""
    
    refresh_token = get_refresh_token(db, token)
    if not refresh_token:
        return False
    
    refresh_token.revoked = True
    db.commit()
    return True   
    

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM]
        )
        print("payload")
        print(payload)

        token_data = userSchema.TokenPayload(**payload)
        print(token_data)
        
        # Verificar que sea un token de acceso
        if token_data.type != "access":
            raise credentials_exception
        
        # Verificar que el token no haya expirado
        # print(datetime.fromtimestamp(token_data.exp))
        print(datetime.now(timezone.utc))
        if token_data.exp < datetime.now(timezone.utc):
            raise credentials_exception
            
    except (jwt.PyJWKError, ValueError):
        raise credentials_exception
        
    user = get_user_by_id(db, token_data.sub)
    if user is None:
        raise credentials_exception


    userSchemaDB = userSchema.User(**user.__dict__)
    return userSchemaDB


def get_current_active_user(
    current_user: Annotated[userSchema.User, Depends(get_current_user)]

):
    if current_user.is_active == False:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def require_role(required_role:str):
    def role_cheker(current_user:userSchema.User=Depends(get_current_active_user),db: Session = Depends(get_db)):

        roles = [rol.rol for rol in current_user.rol]    
          
        print(roles)
        if DefaultRoles.SUPER_ADMIN_ROL in roles and current_user.email=="admin@example.com":
            return current_user
        if required_role not in roles:
            raise HTTPException(status_code=403,detail="Operation not permitted,Not enough permissions")     
        return  current_user
    return  role_cheker

def assign_role(user_rol:User_rol_schema,db:Session=Depends(get_db)):

    validate_rol = db.get(Rol_model,user_rol.rol_id)
    valdiate_user= db.get(UserModel,user_rol.user_id)

    if not validate_rol or not valdiate_user:
        raise HTTPException(status_code=404,detail="User or rol not found")
    
    try:
        rol_user = User_rol(**user_rol.model_dump())
        db.add(rol_user)
        # rol = db.get(Rol,user_rol.rol_id)                   
        db.commit()
        db.refresh(rol_user)
        return rol_user
    except IntegrityError as e :
  
        # rol = db.get(Rol,user_rol.rol_id)   
        print(rol)   
    #     print(e.instance)
    #     print(e._sql_message)
    #     print(e.detail)
    #     # print(e.orig)
        raise HTTPException(detail=f"User already have this role",status_code=400)
    # except Exception as e:
    #     raise HTTPException(detail=e,status_code=400)
    db.refresh(rol_user)