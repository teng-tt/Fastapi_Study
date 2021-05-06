# !/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = "Teng"

from typing import Optional
from fastapi import APIRouter, Depends

app05 = APIRouter()

''' Dependencies 创建，导入和声明依赖'''

#声明
async def common_parameters(q:Optional[str] = None, page:int = 1, limit:int = 100):
    return {"q":q, "page":page, "limit":limit}


#注入
#可以在async def中调用def依赖，也可以在def中调用async def中的依赖
@app05.get("/dependency01")
async def dependency01(commons: dict = Depends(common_parameters)):
    return commons

@app05.get("/deoendency02")
def dependency02(commons: dict = Depends(common_parameters)):
    return commons