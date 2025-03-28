
from fastapi import APIRouter,Depends, HTTPException, status
import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from typing import Annotated
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models.user import User as UserModel
from app.models.rol import Rol as Rol_model
from app.schemas.rol import Rol as Rol_schema
from app.database.database import SessionLocal
from app.schemas import user_team as userSchema
# from app.schemas.rol import DefaultRoles
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
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception       
        user_name = userSchema.TokenData(username=username)
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception
    user = get_user(db, email=user_name.username)
    if user is None:
        raise credentials_exception
    return user


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
        if "Super_admin" in roles and current_user.email=="admin@example.com":
            return current_user
        if required_role not in roles:
            raise HTTPException(status_code=403,detail="Operation not permitted,Not enough permissions")     
        return  current_user
    return  role_cheker

def assign_role(user_rol:User_rol_schema,db:Session=Depends(get_db)):

    validate_rol = db.get(Rol,user_rol.rol_id)
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