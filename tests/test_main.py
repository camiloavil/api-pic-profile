# Pytest
import pytest
# FastAPI
from fastapi import status
from fastapi.testclient import TestClient
# APP
# from app.models import MyModels
# from app.models.user import UserBase, UserFB
# from app.DB.db import get_session
# # SQLModel
# from sqlmodel import Session, create_engine
# # Python
# import os
# import json

from main import app


@pytest.fixture(scope="function")
def client() -> TestClient:
    return TestClient(app)


# #Filename of sqlite DB
# TEST_SQLITE_FILENAME = 'test_DB.sqlite'
# BASE_DIR = os.path.dirname(os.path.realpath(__file__))
# DATABASE_URL = f'sqlite:///{os.path.join(BASE_DIR,TEST_SQLITE_FILENAME)}' 
# test_engine = create_engine(DATABASE_URL, echo = False)

# def setnew_dbTesting():
#     os.remove(os.path.join(BASE_DIR, TEST_SQLITE_FILENAME))
#     SQLModel.metadata.create_all(test_engine)

# def get_test_session():
#     with Session(test_engine) as session:
#         yield session

# app.dependency_overrides[get_session] = get_test_session


def test_home_item(client: TestClient):
    # response = client.get("/items/foo", headers={"X-Token": "coneofsilence"})
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
