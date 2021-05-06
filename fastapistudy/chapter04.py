# !/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = "Teng"

from fastapi import APIRouter, status, Form, File, UploadFile, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Union
from enum import Enum

app04 = APIRouter()

'''Response Model 响应模型'''

class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr
    mobile: str = "10086"
    address: str = None
    full_name: Optional[str] = None


class UserOut(BaseModel):
    username: str
    email: EmailStr  # 用到EmailStr 需要pip install pydantic[email]
    mobile: str = "10086"
    address: str = None
    full_name: Optional[str] = None

users = {
    "user01": {"username": "user01", "password": "123123", "email": "axsa@aa.com"},
    "user02":{"username": "user02", "password": "123asda123", "email": "asadsxsa@aa.com", "mobile": "1001001010"},
}

@app04.post("/response_model", response_model=UserOut, response_model_exclude_unset=True)
async def response_model(user: UserIn):
    '''
    response_model_exclude_unset=True表示默认值不包含在响应中，仅包含实际给的值，如果实际给的值与默认值相同也会包含在响应中
    :param user:
    :return:
    '''
    print(user.password) #password不会被返回
    return users["user02"]

class StudentData(BaseModel):
    name: str
    address: Optional[str] = None
    classmate: str

class Six(str, Enum):
    boy = "boy"
    girls = "girls"

@app04.post("/studentdata")
def student_data(studentdate: StudentData, six: Six):
    if six.boy == "boy":
        return {"name": studentdate.name, "six": six.boy, "address": studentdate.address, "classmate": studentdate.classmate }
    else:
        return {"name": studentdate.name, "six": six.girls, "address": studentdate.address, "classmate": studentdate.classmate }

@app04.post(
    "/response_model/attributes",
    # response_model=UserOut,
    response_model=Union[UserIn, UserOut]
    # response_model=List[UserOut],
    # response_model_include=["username", "email", "mobile"],
    # response_model_exclude=["mobile"]
)

async def response_model_attributes(user: UserIn):
    '''
    response_model_include 列出需要在返回结果中的字段
    response_model_exclude 列出不需要在返回结果的字段

    :param user:
    :return:
    '''
    # del user.password # Union[UserIn, UserOut]后，区2个属性的并集返回并集结果
    # return user
    return [user, user]

'''  Response Status Code响应状态码'''
@app04.post("/status_code", status_code=200)
async  def status_code():
    return {"status_code": 200}

@app04.post("status_attribute", status_code=status.HTTP_200_OK)
async  def status_attribute():
    return {"status_attribute": status.HTTP_200_OK}


''' Form Data 表单数据'''
@app04.post("/login")
async def login(username: str = Form(...), password: str = Form(...)): #定义表单参数
    '''
      用from类需要pip install python-multipart
      from类元数据校验方法类似Body/Query/Path/Cookie等
    :param username:
    :param password:
    :return:
    '''
    return {"username": username}

''' Rqquest File 单文件，多文件上传及参数详解'''

@app04.post("/file")
async def file_(file: List[bytes] = File(...)):  #列表形式可以上传多个文件
    '''
        使用file类。文件内容会以bytes的形式读入内存，适合于上传小文件
    :param file:
    :return:
    '''
    return {"file_size": len(file)}

@app04.post("/uplode_file")
async def uplode_file(files: List[UploadFile] = File(...)): #上传单个文件去掉list就行
    '''
        如果使用UplodeFile类的优势
        1.文件存储在内存中，使用内存达到阈值后，将被保存在磁盘中
        2.适合于图片，视频文件
        3.可以获取上传文件的元数据，如文件名，创建时间等
        4.有文件对象的异步接口
        5.上传的文件是python文件对象，可以使用wirte(), read(), seek(), close()操作
    :param file:
    :return:
    '''
    for file in files:
        contents = await file.read()
        print(contents)
    return {"filename": files[0].filename, "content_type": files[0].content_type}

''' FastApi项目的静态文件配置见 run.py'''

''' 路径操作配置'''
@app04.post(
    "/path_operation_configuration",
    response_model=UserOut,
    #tags=["Path", "Operation", "Configuration"],
    summary="This is summary",
    description="This is description",
    response_description="This is response description",
    deprecated=True,
    status_code=status.HTTP_200_OK
)
async def path_operatin_configration(user: UserIn):
    '''
    Path Operation Configuration
    :param user: 用户信息
    :return: 返回结果
    '''
    return user.dict()


''' FastApi应用常见配置见run.py'''

''' FastApi 框架的错误处理'''

@app04.get("/http_exception")
async def http_exception(city: str):
    if city != "Beijing":
        raise HTTPException(status_code=404, detail="City not found!", headers={"X-Erroe":"Error"})
    return {"city": city}

@app04.get("/http_exception/{city_id}")
async def override_http_exception(city_id: int):
    if city_id == 1:
        raise HTTPException(status_code=418, detail="Nopr! I don't like 1.")
    return {"city": city_id}

