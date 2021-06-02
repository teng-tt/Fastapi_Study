# !/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = "Teng"

from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException


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

''' 类作为依赖引入 '''

fake_items_db = [{"item_name":"xx"},{"item_name":"yy"},{"item_name":"dd"}]

class CommonQueryParams:
    def __init__(self, q: Optional[str]=None, page: int = 1, limit: int = 100):
        self.q = q
        self.page = page
        self.limit = limit

@app05.get("/classes_as_dependencies")
#一下三种写法都可以，这里采用最简单的一种写法
#async def classes_as_dependencies(commons: CommonQueryParams = Depends(CommonQueryParams)):
#async def classes_as_dependencies(commons: CommonQueryParams = Depends()):
async def classes_as_depnedencies(commons=Depends(CommonQueryParams)):
    response = {}
    if commons.q:
        response.update({"q":commons.q})
    items = fake_items_db[commons.page: commons.page + commons.limit]
    response.update({"items": items})
    return  response


''' Sub-dependencies 子依赖'''

def query(q: Optional[str] = None):
    return q

def sub_query(q: str = Depends(query), last_query: Optional[str] = None):
    if not q:
        return q
    return q

@app05.get("/sub_dependency")
async def sub_dependency(final_query: str = Depends(sub_query, use_cache=True)):
    '''
    use_cache 默认是True，表示当多个依赖有一个共同的子依赖时,每次request请求只会调用子依赖一次，其它使用缓存，提升性能
    :param final_query:
    :return:
    '''
    return {"final_query": final_query}


''' 路径操作装饰器中的多依赖 '''
async def verify_token(x_token: str = Header(...)):
    '''
    没有返回值的子依赖
    :param x_token:
    :return:
    '''
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")
    return x_token

async def verify_key(x_key: str = Header(...)):
    '''
    有返回值的子依赖,但是返回值不会被调用
    :param x_key:
    :return:
    '''
    if x_key != "fake-super-secret-key":
        raise HTTPException(status_code=400, detail="X-Key header invalid")
    return x_key

''' 路径操作装饰器中的多依赖 '''
@app05.get("/dependency_in_path_operation", dependencies=[Depends(verify_token), Depends(verify_key)])
async def dependency_in_path_operation():
    return [{"user":"xx"}, {"user1":"yy"}]

''' 全局依赖 '''
# 可以在整个程序中使用，如需要在所有的5的所有接口中校验上面的token与key
#app05 = APIRouter(dependencies=[Depends(verify_token), Depends(verify_key)])

''' Dependencies with yield 带yield的依赖'''
#以下是对数据库的连接伪代码

async def get_db():
    db = "db_connetion"
    try:
        yield db
    finally:
        db.endswith("db_close")

async def dependency_a():
    dep_a = "generate_dep_a()"
    try:
        yield dep_a
    finally:
        dep_a.endswith("db_close")

async def dependency_b(dep_a=Depends(dependency_a)):
    dep_b = "generate_dep_b()"
    try:
        yield dep_b
    finally:
        dep_b.endswith(dep_a)

async def dependency_c(dep_b=Depends(dependency_b)):
    dep_c = "generate_dep_c()"
    try:
        yield dep_c
    finally:
        dep_c.endswith(dep_b)