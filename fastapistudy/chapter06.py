# !/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = "Teng"

from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app06 = APIRouter()

''' OAuth2 密码模式和 FastAPI 的OAuth2PasswordBearer '''

'''
OAuth2PasswordBearer是接收url作为参数的一个类，客户端会向该url发送
passworld，username参数，然后得到一个token值
OAuth2PasswordBearer并不会创建相应的url路径操作，只是指明客户端用来请求token的url地址
当请求到来的时候，FastApi会检查侵权的Authorization头信息，如果没有找到Authorization头信息
或者头信息不是Bearer token，它会返回401状态码（UNAUTHORIZED）
'''
#请求token的url地址=http://127.0.0.0:8000/chapter06/token
oauth2_schema = OAuth2PasswordBearer(tokenUrl='/chapter06/token')

@app06.get("/oauth2_password_bearer")
async def oauth2_password_bearer(token: str = Depends(oauth2_schema)):
    return {"token": token}


''' 基于password 和 Bearer token的OAuth2认证'''

fake_users_db = {
    "jox":{
        "username":"jox",
        "full_name":"jox x",
        "email":"jox@126.com",
        "hashed_password":"fakehashedxx",
        "disabled":False,
    },
    "joy":{
        "username":"joy",
        "full_name":"joy y",
        "email":"joy@126.com",
        "hashed_password":"fakehashedyy",
        "disabled":True,
    },
}


def fake_hashed_password(password: str):
    return "fakehashed" + password

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    hashed_password: str


def get_user(db, username: str):
        if username in db:
            user_dict = db[username]
            return UserInDB(**user_dict)

def fake_decode_token(token: str):
    user = get_user(fake_users_db, token)
    return user


async def get_current_user(token: str = Depends(oauth2_schema)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"} #OAuth2的规范，如果认证失败，请求头中返回"WWW-Authenticate"
        )
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user "
        )
    return current_user


@app06.post("/token")
def login(from_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_users_db.get(from_data.username)
    if not user_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password"
        )
    user = UserInDB(**user_dict)
    hashed_password = fake_hashed_password(from_data.password)
    if not hashed_password == user.hashed_password:
        pass
    return {"access_token": user.username, "token_type": "bearer"}


@app06.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user