# !/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = "Teng"

from fastapi import APIRouter, Path, Query, Cookie, Header
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import date
from enum import Enum

app03 = APIRouter()

'''路径参数和数字验证'''
# 函数的顺序就是路由的顺序 路由的优先级,如果优先的匹配了，后面的就不会在匹配这点要注意

@app03.get("/path/parameters")
def path_params01():
    return {"message": "The is a message"}


# {}里面为路径参数的名称，在函数中调用该路径参数，函数参数的名称必须与路径参数的名称一致
@app03.get("/path/{parameters}")
def path_params01(parameters: str):
    return {"message": parameters}

class CityName(str, Enum):
    Beijing = "Beijing China"
    Shanghai = "Shanghai China"


# 枚举类型参数
@app03.get("/enum/{city}")
async def latest(city: CityName):
    if city == CityName.Shanghai:
        return {"city_name": city, "confirmed": 1492, "death": 7}
    if city == CityName.Beijing:
        return {"city_name": city, "confirmed": 1301, "death": 9}
    return {"city_name": city, "latest": "unknown"}


# 通过path parameters传递文件路径，其中path标记会将file_path中的冲突/识别为url中的、，不加就会有冲突
@app03.get("/files/{file_path:path}")
def filepath(file_path: str):
    return f"the file path is {file_path}"


# 路径参数数据校验
@app03.get("/path/{num}")
def path_params_validate(
        num: int = Path(..., title="Yor number", description="不可描述", ge=1, le=10)
):
    return num


'''查询参数和字符串验证'''
@app03.get("/query")
def page_limit(page: int = 1, limit: Optional[int] = None):
    if limit:
        return {"page": page, "limit": limit}
    return {"page": page}


# bool类型转换: yes on 1 可以转换为 True,其它的会为false或者报错
@app03.get("/query/bool/conversion")
def type_conversion(param: bool = False):
    return param


# 多个查询参数的列表，参数别名
@app03.get("/query/validations")
def query_params_validate(
        value: str = Query(..., min_length=8, max_length=16, regex="^a"),
        values: List[str] = Query(default=["v1", "v2"], alias="alias_name")
):
    return value, values


'''请求体和字段，多参数混合'''


# 请求体
class CityInfo(BaseModel):
    name: str = Field(..., example="Beijing") #example值做注解作用值不会被验证
    country: str
    country_code: str = None #给一个默认值
    country_population: int = Field(default=800, title="人口数量", description="国家人口数量", ge=800)

    class Config:
        schema_extra = {
            "example":{
                "name": "Shanghai",
                "country": "China",
                "country_code": "CN",
                "country_population": 1400000,
            }
        }

@app03.post("/request_body/city")
def city_info(city: CityInfo):
    print(city.name, city.country)
    return city.dict()

# 混合参数
@app03.put("/request_body/city/{name}")
def mix_city_info(
    name: str,
    city01: CityInfo, #Body 可以定义多个的
    city02: CityInfo,
    confirmed: int = Query(ge=0, description="确诊数", default=0),
    death: int = Query(ge=0, description="死亡数", default=0)
):
    if name == "Shanghai":
        return {"Shanghai": {"confirmed": confirmed, "death": death}}
    return city01.dict(), city02.dict()

# 数据格式嵌套的请求体
# 请求体要对字段进行校验使用pydantic的 Field
# 要对路径参数进行校验使用Path
# 要对查询参数进行校验使用Query
class Data(BaseModel):
    city: List[CityInfo] = None
    date: date
    confirmed: int = Field(ge=0, description="确诊数", default=0)
    deaths: int = Field(ge=0, description="死亡数", default=0)
    recovered: int = Field(ge=0, description="痊愈数", default=0)

@app03.put("/request_body/nested")
def nested_models(data: Data):
    return data

'''Cookie 和 Header参数'''

# 效果只能用Postman测试
# 定义Cookie参数需要使用Cookie类
@app03.get("/cookie")
def cookie(cookie_id: Optional[str] = Cookie(None)):
    return {"cookie_id": cookie_id}

@app03.get("/header")
def header(user_agent: Optional[str] = Header(None, convert_underscores=True),  x_token: List[str] = Header(None)):
    """
    有些HTTP代理和服务器是不允许在请求头中带有下划线的，所以Header提供convert_underscores参数=True可以解决
    :param user_agent: convert_underscores=True 会把 user_agent 变成 user-agent
    :param x_token: x_token是包含多个值的列表
    :return:
    """
    return {"User-Agent": user_agent, "x_token": x_token}