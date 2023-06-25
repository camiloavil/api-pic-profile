#FastAPI
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import Body
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
#SQLModel
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
# APP
from app.models.user import User, UserNew, UserLogin, UserFB
from app.DB.db import get_session, engine
# passlib
from passlib.context import CryptContext
#jose
from jose import jwt, JWTError
# Python
from typing import Annotated, Union
from datetime import datetime, timedelta
from pydantic import BaseModel


SECRET_KEY = "54f12eb620bc1495166793b5d38d29b0468ef97d33c92eb1fcc0a6de916816d7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Token(BaseModel):
    access_token: str
    token_type: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

users_router = APIRouter()

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str):
    return pwd_context.hash(password.encode('utf-8'))

def get_user_db(username: str):
    with Session(engine) as session:
        statement = select(User).where(User.email == username)
        user_db = session.exec(statement).first()

    if user_db is None:
        return None
    return user_db

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=5)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"},)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_db(username=username)
    if user is None:
        raise credentials_exception
    return user

@users_router.get(path="/myuser/",
                  response_model=UserFB,
                  tags=["Trys"])
async def info_User(current_user: Annotated[User, Depends(get_current_user)]):
    """
    Get information about the current user.

    :return: UserFB - Information about the current user
    """
    return UserFB(**current_user.dict())


@users_router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                session: Session = Depends(get_session)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"},)
    user_db = get_user_db(form_data.username)

    if user_db is None:
        raise credentials_exception
    if not verify_password(form_data.password, user_db.pass_hash):
        raise credentials_exception
    access_token = create_access_token(data={"sub": user_db.email}, 
                                       expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}



@users_router.get(path="/users", 
                 response_model=list[UserFB], 
                 tags=["Users"])
def get_users(session: Session = Depends(get_session)):
    print("get_users")
    all_users = session.query(User).all()
    print(all_users)
    all_users = [UserFB(**user.dict()) for user in all_users]
    print(all_users)
    
    return all_users

@users_router.post(path="/new_user",
                  response_model=UserFB,
                  tags=["Users"],
                  status_code=status.HTTP_201_CREATED)
def create_user(user: UserNew = Body(...),
                session: Session = Depends(get_session)):
    user_dict = user.dict()
    user_dict.update({"pass_hash": get_password_hash(user.password.get_secret_value())})
    new_user = User(**user_dict)
    
    try:
        user_db = User.from_orm(new_user)
        session.add(user_db)
        session.commit()
        session.refresh(user_db)
        print(str(user_db))
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    except Exception as e:
        print("Error Creating User:"+str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return UserFB(user_id=new_user.user_id, name=user.name, email=user.email)
    # return JSONResponse(status_code=status.HTTP_201_CREATED,content={'message' : 'User added', 'id' : user_db.id, 'username' : user_db.name })

@users_router.get(path="/users/me/", 
                  response_model=UserFB,
                  tags=["Users"])
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user

@users_router.post(path="/logintest",
                  response_model=UserFB,
                  tags=["Users"],
                  status_code=status.HTTP_200_OK)
def loginTest(user: UserLogin = Body(...),
          session: Session = Depends(get_session)):
    user_db = session.query(User).filter(User.email == user.email).first()
    
    if user_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if not verify_password(user.password.get_secret_value(), user_db.pass_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return UserFB(**user_db.dict())