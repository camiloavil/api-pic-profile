#FastAPI
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import Body
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
#SQLModel
from sqlmodel import Session
from sqlalchemy.exc import IntegrityError
# APP
from app.models.user import User, UserNew, UserLogin, UserFB
from app.DB.db import get_session
# passlib
from passlib.context import CryptContext
# Python
from typing import Annotated

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

users_router = APIRouter()

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_password_hash(password: str):
    return pwd_context.hash(password.encode('utf-8'))


def fake_decode_token(token):
    print (f'fake_decode_token: {token}')
    return User(username=token + "fakedecoded", email="john@example.com")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    return user

@users_router.get(path="/myuser/",
                  tags=["Trys"])
async def read_items(current_user: Annotated[User, Depends(get_current_user)]):
    print(str(current_user))
    return current_user

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

@users_router.post(path="/login",
                  response_model=UserFB,
                  tags=["Users"],
                  status_code=status.HTTP_200_OK)
def login(user: UserLogin = Body(...),
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