# Pytest
import pytest
# FastAPI
from fastapi import status
from fastapi.testclient import TestClient
# APP
from app.models.user import SQLModel, UserBase, UserFB
from app.DB.db import get_session
# SQLModel
from sqlmodel import Session, create_engine
# Python
import os
import json

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

# class TestUsers:
#     def test_create_newuser_blank(self):
#         response = client.post("/users/newuser")
#         assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
#         # assert response.json() == {'detail': [{'loc': ['body'],
#         #                                         'msg': 'field required',
#         #                                         'type': 'value_error.missing'}]}

#     def test_create_newuser_all_fields(self):
#         setnew_dbTesting()
#         params = {
#             "name": "Testing",
#             "email": "test@example.com",
#             "password": "MyPassword",
#             "city": "TestyCity",
#             "country": "Testland"
#             }
#         response = client.post("/users/newuser",json=params,)
#         params.pop('password')  # remove password it never should be returned
#         params['userType'] = 'free'
#         assert response.status_code == status.HTTP_201_CREATED, "Status code not 201"
#         assert isinstance(response.json(), dict), "Response is not a dictionary"
#         assert all(key in response.json() for key in params) , "Response Incomplete"
#         assert UserBase(**response.json()) == UserBase(**params), "User created is different" 
#         assert 'pass_hash' not in response.json() , "pass_hash Should never be in the response"

#     def test_create_newuser_(self):
#         setnew_dbTesting()
#         params = {
#             "name": "Testing",
#             "email": "test@example.com",
#             "password": "MyPassword"
#             }
#         response = client.post("/users/newuser",json=params,)
#         params.pop('password')  # remove password it never should be returned
#         params['userType'] = 'free'
#         assert response.status_code == status.HTTP_201_CREATED, "Status code not 201"
#         assert isinstance(response.json(), dict), "Response is not a dictionary"
#         assert all(key in response.json() for key in params) , "Response Incomplete. it hasn't all keys"
#         assert UserBase(**response.json()) == UserBase(**params), "User created is different" 
#         assert 'pass_hash' not in response.json() , "pass_hash Should never be in the response"

#     def test_create_newuser_usertype_be_free(self):
#         setnew_dbTesting()
#         params = {
#             "name": "Testing",
#             "email": "test@example.com",
#             "password": "MyPassword",
#             "userType": "admin"
#             }
#         response = client.post("/users/newuser",json=params,)
#         params.pop('password')  # remove password it never should be returned
#         # params['userType'] = 'free'
#         assert response.status_code == status.HTTP_201_CREATED, "Status code not 201"
#         assert isinstance(response.json(), dict), "Response is not a dictionary"
#         assert all(key in response.json() for key in params) , "Response Incomplete. it hasn't all keys"
#         assert response.json()['userType'] == 'free', "new users userType always should be free" 

#     def test_create_newuser_repeted(self):
#         setnew_dbTesting()
#         params = {
#             "name": "Testing",
#             "email": "test@example.com",
#             "password": "MyPassword"
#             }
#         client.post("/users/newuser",json=params,)
#         response = client.post("/users/newuser",json=params,)

#         assert response.status_code == status.HTTP_409_CONFLICT, "Status code not 409 Conflict"

#     def test_info_user_path_without_credentials(self):
#         # response = client.get("/items/foo", headers={"X-Token": "coneofsilence"})
#         response = client.get("/users/myuser")
#         assert response.status_code == status.HTTP_401_UNAUTHORIZED, "Status code not 401 on path GET /users/myuser"

#         response = client.put("/users/myuser")
#         assert response.status_code == status.HTTP_401_UNAUTHORIZED, "Status code not 401 on path PUT /users/myuser"

#         response = client.delete("/users/myuser")
#         assert response.status_code == status.HTTP_401_UNAUTHORIZED, "Status code not 401 on path DELETE /users/myuser"

#         response = client.put("/users/myuser/changepassword")
#         assert response.status_code == status.HTTP_401_UNAUTHORIZED, "Status code not 401 on path PUT /users/myuser/changepassword"

#     def test_login_user_must_be_same_user(self):
#         # response = client.get("/items/foo", headers={"X-Token": "coneofsilence"})
#         setnew_dbTesting()
#         #create users
#         user1 = {"name": "Uno Name", "email": "uno@example.com", "password": "MyPassword1"}
#         user2 = {"name": "Dos Name", "email": "dos@example.com", "password": "MyPassword2"}
#         client.post("/users/newuser",json=user1,)
#         client.post("/users/newuser",json=user2,)
#         dataLoginError = {'username': 'value1', 'password': 'value2'}
#         response = client.post("/userlogin", data=dataLoginError)
#         assert response.status_code == status.HTTP_401_UNAUTHORIZED, "Status code not 401 on path GET /users/myuser"

#         dataLogin1 = {'grant_type':'',
#                       'scope':'',
#                       'client_id':'',
#                       'client_secret':'',
#                       'username': user1["email"], 'password': user1["password"]}
        
#         dataLogin = {'username': user1["email"], 'password': user1["password"]}
#         print(str(dataLogin))
#         responseToken = client.post("/userlogin", 
#                                     headers={"Accept": "application/json",
#                                              "Content-Type": "application/x-www-form-urlencoded"}, 
#                                     data=dataLogin)
#                                     # json=dataLogin1)
#         print(str(responseToken.json()))
#         assert response.status_code == status.HTTP_200_OK, "Status code must be 200"
#         assert 'access_token' in responseToken.json(), "access_token must be in Correct Response"
#         # tokeUser1 = responseToken.json()['access_token']

        