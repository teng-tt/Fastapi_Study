# !/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = "Teng"

from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt


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
        "hashed_password":"$2a$10$maj8eisFrJJOrK4tcKzhAeD2ejIx2nE/ETiRMsKh6gxkv6GVAM3qG",
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


@app06.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password"
        )
    user = UserInDB(**user_dict)
    hashed_password = fake_hashed_password(form_data.password)
    if not hashed_password == user.hashed_password:
        pass
    return {"access_token": user.username, "token_type": "bearer"}


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


@app06.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


''' 基于json web token的认证 '''

#名文passwoed = asxaxAXZaas
fake_users_db.update({
    "john snow":{
        "username": "john snow",
        "full_name": "John Snow",
        "email": "johnsnow@126.com",
        "hashed_password": "$2a$10$GxvPPj/C/BYoiH9GmIoMheMFqdkvEup/o3fZQRqYtuGjp2AOLTWLC",
        "disabled": False,
    }
})

# 生成秘钥 openssl rand -hex 32
SECRET_KEY = "e8f4be91317c64f22599a8022524721085ee2812e3351fcb1467f60e446818d3"
ALGORITHM = "HS256"  #算法
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # 访问令牌过期分钟


class Token(BaseModel):
    '''返回给用户的Token'''
    access_token: str
    token_type: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/chapter06/jwt/token")

def verity_password(plain_password: str, hashed_password: str):
    '''对密码进行校验,返回true或者false'''
    return pwd_context.verify(plain_password, hashed_password)

def jwt_get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def jwt_authenticate_user(db, username: str, password: str):
    user = jwt_get_user(db=db, username=username)
    if not user:
        return False
    if not verity_password(plain_password=password, hashed_password=user.hashed_password):
        return False
    return user


def created_access_token(data: dict, expires_delta: Optional[timedelta]=None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(claims=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app06.post("/jwt/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm=Depends()):
    user = jwt_authenticate_user(db=fake_users_db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = created_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "Bearer"}


async def jwt_get_current_user(token: str = Depends(oauth2_schema)):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        playload = jwt.decode(token=token, key=SECRET_KEY, algorithms=ALGORITHM)
        username = playload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = jwt_get_user(db=fake_users_db, username=username)
    if user is None:
        raise credentials_exception

    return user


async def jwt_get_current_active_user(current_user: User=Depends(jwt_get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

@app06.get("/jwt/users/me")
async def jwt_read_users_me(current_user: User=Depends(jwt_get_current_active_user)):
    return current_user


