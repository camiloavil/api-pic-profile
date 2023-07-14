# pytest
import pytest
# FastAPI
from fastapi.testclient import TestClient
# from httpx import AsyncClient
# APP
from app.models import MyModels
from app.models.user import User, UserBase, UserFB, UserUpdate
from app.security.secureuser import get_password_hash
from app.DB.db import get_session
from app.DB.querys_users import add_user_to_db
# SQLModel
from sqlmodel import Session, create_engine
# Python
import os

from main import app

#Filename of sqlite DB
TEST_SQLITE_FILENAME = 'test_DB.sqlite'
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
DATABASE_URL = f'sqlite:///{os.path.join(BASE_DIR,TEST_SQLITE_FILENAME)}' 
test_engine = create_engine(DATABASE_URL, 
                            connect_args={'check_same_thread': False}, 
                            echo = False)
MyModels.metadata.create_all(test_engine)

def delete_db_file():
    os.remove(os.path.join(BASE_DIR, TEST_SQLITE_FILENAME))

def get_test_session():
    with Session(test_engine) as session:
        yield session

app.dependency_overrides[get_session] = get_test_session

@pytest.fixture(scope="class")
def client() -> TestClient:
    # MyModels.metadata.drop_all(test_engine)
    MyModels.metadata.create_all(test_engine)
    yield TestClient(app)
    delete_db_file()

@pytest.fixture(scope="class")
def setUp_users():
    user1 = {
        "name": "Test user One",
        "email": "one@example.com",
        "password": "MyPassword",
        "city": "TestyCity",
        "country": "Testland",
        "userType": "admin"
        }
    user2 = {
        "name": "Test user Two",
        "email": "two@example.com",
        "password": "MyPassword",
        "city": "TestyCity",
        "country": "Testland",
        "userType": "test"
        }
    user3 = {
        "name": "Test user Tree",
        "email": "tree@example.com",
        "password": "MyPassword",
        "city": "TreeCity",
        "country": "Treeland",
        "userType": "test"
        }
    with Session(test_engine) as session:
        add_user_to_db(User(**user1, pass_hash= get_password_hash(user2["password"])),
                       session)
        add_user_to_db(User(**user2, pass_hash= get_password_hash(user2["password"])),
                       session)
        add_user_to_db(User(**user3, pass_hash= get_password_hash(user3["password"])),
                       session)
    yield user1,user2,user3
