
from fastapi import APIRouter,Depends, HTTPException, status
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from models.user import User as UserModel
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from database.database import SessionLocal

from schemas import user as userSchema

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/User/token")
SECRET_KEY = "09d25e095faa6ca2556c818167b7a9563b93f7099f6f0f4caa6cf63b88e8d3e8"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30



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
    userSchemaDB = userSchema.User(**current_user.__dict__)
    return userSchemaDB
 


def authenticate_user( email: str, password: str,db: Session = Depends(get_db)):
    user =  db.query(UserModel).filter(UserModel.email == email).first()

    if not user:
        return False
    if not verify_password(password, user.password):
        return False
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


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],db: Session = Depends(get_db)):
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(token)
        username: str = payload.get("sub")
        print(username)
        if username is None:
            raise credentials_exception       
        # user = db.query(UserModel).filter(UserModel.email == username).first()
        # userFinal = userSchema.User(**user.__dict__)
        user_name = userSchema.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, email = user_name.username)
    if user is None:
        raise credentials_exception
    print(user)
    return user


def get_current_active_user(
    current_user: Annotated[userSchema.User, Depends(get_current_user)]

):
    if current_user.is_active == False:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
