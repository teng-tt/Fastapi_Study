# !/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = "Teng"

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()  # 这里名字不一定是app,名字随意

class CityInfo(BaseModel):
    province: str
    country: str
    is_affected: Optional[bool] = None # 与bool的区别是可以不传，默认是null
    #is_affected: bool   改参数的话为必须传递的

# @app.get('/')
# def hello_world():
#     return {'hello': 'world'}
#
# @app.get('/city/{city}')  #使用参数话传递  {city}为参数的名字
# def result(city: str, query_string: Optional[str] = None):  #city为上面city传递过来的参数，str类型
#     return {'city': city, 'query_string': query_string}
#
# @app.put('/city/{city}')
# def result(city: str, city_info: CityInfo):
#     return {"city": city, 'country': city_info.country, 'is_affected': city_info.is_affected}


# 使用异步方式
@app.get('/')
async def hello_world():
    return {'hello': 'world'}

@app.get('/city/{city}')  #使用参数话传递  {city}为参数的名字
async def result(city: str, query_string: Optional[str] = None):  #city为上面city传递过来的参数，str类型
    return {'city': city, 'query_string': query_string}

@app.put('/city/{city}')
async def result(city: str, city_info: CityInfo):
    return {"city": city, 'country': city_info.country, 'is_affected': city_info.is_affected}

# 启动命令 uvicorn hello_world:app   --reload