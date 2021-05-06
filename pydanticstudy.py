# !/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = "Teng"

from pydantic import BaseModel, ValidationError, constr
from datetime import datetime, date
from typing import List, Optional
from pathlib import Path
from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base

'''
Data validation and settings management using python type annotations.
使用Python的类型注解来进行数据校验和settings管理
pydantic enforces type hints at runtime, and provides user friendly errors when data is invalid.
Pydantic可以在代码运行时提供类型提示，数据校验失败时提供友好的错误提示
Define how data should be in pure, canonical python; validate it with pydantic.
定义数据应该如何在纯规范的Python代码中保存，并用Pydantic验证它
'''

print("\033[31m1. --- Pydantic的基本用法。Pycharm可以安装Pydantic插件 ---\033[0m")

class User(BaseModel):
    id: int    # 必填字段,没有默认值
    name: str = "Teng"  # 有默认值选填字段
    singnup_ts: Optional[datetime] = None
    friends: List[int] = [] # 列表中的元素是int类型或者可以直接转换成int类型

external_data = {
    "id": "123",
    "singnup_ts": "2022-12-22 12:22",
    "friends": [1,2,3,"6"] # 6是可以转换成整型int(3)的
}

user = User(**external_data) #实例化调用
print(user.id, user.friends)
print(repr(user.singnup_ts))
print(user.dict())

print("\033[31m2. --- 校验失败处理 ---\033[0m")
try:
    User(id=1, singnup_ts=datetime.today(), friends=[1, 2, "not number"])
except ValidationError as e:
    print(e.json())

print("\033[31m3. --- 模型类的的属性和方法 ---\033[0m")
print(user.dict())
print(user.json())
print(user.copy())   # 浅拷贝
print(User.parse_obj(obj=external_data))
print(User.parse_raw('{"id": 123, "name": "Teng", "singnup_ts": "2022-12-22T12:22:00", "friends": [1, 2, 3, 6]}'))

path = Path("test.json")
path.write_text('{"id": 123, "name": "Teng", "singnup_ts": "2022-12-22T12:22:00", "friends": [1, 2, 3, 6]}')
print(User.parse_file(path))
print(user.schema())
print(user.schema_json())
print(user.construct())   # 不校验数据，直接创建模型类，不建议在该方法传入为知数据，不安全
print(User.__fields__.keys()) #定义模型类的时候。所有字段都注明类型，字段顺序就不会乱

print("\033[31m4. --- 递归模型 ---\033[0m")
# 递归模型
class Sound(BaseModel):
    sound : str

class Dog(BaseModel):
    birthday: date
    weight: float = Optional[None]
    sound: List[Sound]  # 不同的狗有不同的叫声，递归模型，就是一个嵌套一个

dog = Dog(birthday=datetime.today(), weight=6.66, sound=[{"sound":"wangwnag"}, {"sound":"yingying"}])
print(dog.dict())

print("\033[31m5. --- ORM模型：从类实例创建符合ORM对象的模型  ---\033[0m")
Base = declarative_base()

class CompanyOrm(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, nullable=False)
    public_key = Column(String(20), index=True, nullable=False, unique=True)
    name = Column(String(63), unique=True)
    domains = Column(ARRAY(String(255)))

class CompanyModel(BaseModel):
    id: int
    public_key: constr(max_length=20)
    name: constr(max_length=63)
    domains: List[constr(max_length=255)]

    class Config:
        orm_mode = True

co_orm = CompanyOrm(
    id=123,
    public_key='foobar',
    name='Testing',
    domains=['ex.com', 'xx.com', 'ggg.com']
)

print(CompanyModel.from_orm(co_orm))

print("\033[31m6. --- Pydantic支撑的字段类型  ---\033[0m")  # 官方文档：https://pydantic-docs.helpmanual.io/usage/types/
