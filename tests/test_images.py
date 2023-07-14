# pytest
import pytest
# FastAPI
from fastapi import status
from httpx import AsyncClient
# SQLModel
from sqlmodel import Session
# APP
from app.DB.querys_pictures import PictureDB as PicDB
from app.DB.querys_pictures import FreePictureDB as FreePicDB
# from app.models.user import User, UserBase, UserFB, UserUpdate
# Testing
from .conftest import app, client, test_engine
# Python
import os

TEST_DIR = os.path.dirname(os.path.realpath(__file__))


class TestFreePicture:
    def test_getFreePicture_whitout_picture(self, client: client):
        response = client.post("/pictures/example")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, "Route whitout Picture"  # noqa: E501

    # @pytest.mark.anyio
    # def test_getFreePicture(self, client: client):
    #     # data = {'message': 'Hello, world!'}
    #     files={'picture_file': open(os.path.join(TEST_DIR,'images/testing.jpg'), 'rb')}
    #     # response = client.post("/pictures/example", data=data, files=files) 
    #     # async with AsyncClient(app=app, base_url="http://test") as ac:
    #     #     response = await ac.post("/pictures/example", files=files) 
    #     response = client.post("/pictures/example", files=files) 
    #     # print(response.text)
    #     print(response.url)
    #     assert response.status_code == status.HTTP_200_OK, "Picture returned successfully"  # noqa: E501
    #     # assert response.status_code == status.HTTP_400_BAD_REQUEST, "Picture returned successfully"  # noqa: E501

    @pytest.mark.asyncio
    async def test_async_getFreePicture(self,):
        with Session(test_engine) as session:
            freePics = FreePicDB.get_picture_ip("127.0.0.1", session)
            print(freePics)

        files={'picture_file': open(os.path.join(TEST_DIR,'images/testing.jpg'), 'rb')}
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/pictures/example", files=files) 
            assert response.status_code == status.HTTP_200_OK, "Picture returned successfully"  # noqa: E501
            assert response.headers['content-type'] == 'image/png', "Returned content-type is not image/png"  # noqa: E501
        with Session(test_engine) as session:
            freePics = FreePicDB.get_picture_ip("127.0.0.1", session)
            print(freePics)
        # This request must create a nee register on DB
        # print(str(response.))
        # assert response.json() == {"message": "Tomato"}, "Error to print stout"

class TestHome:
    def test_home_item(self, client: client): 
        # response = client.get("/items/foo", headers={"X-Token": "coneofsilence"})
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
