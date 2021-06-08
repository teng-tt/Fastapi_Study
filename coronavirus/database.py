# !/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = "Teng"

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = 'sqlite:///./coronavirus.sqlite3'
#mysql连接方法
#SQLALCHEMY_DATABASE_URL = 'mysql://username:password@host:port/database_name'

engin = create_engine(
    # echo=True 表示引擎将用repr()函数记录所有语句及其参数列表到日志
    # 由于SQLAlchemy是多线程，指定check_same_thread=False来让建立的对象任意线程都可使用，这个参数只在使用SQLite时设置
    SQLALCHEMY_DATABASE_URL, encoding = 'utf-8', echo=True, connect_args = {'check_same_thread': False}
)

#在SQLAlchemy中，CRUD都是通过会话（session）进行的，所以我们必须要先创建会话，每一个SessionLocal实例就是一个数据库的session
#flush()是指发送数据库语句到数据库，但数据库不一定执行写入磁盘，commit()是指提交事务，将变更保存到数据库文件
SessionLocal = sessionmaker(bind=engin, autoflush=False, autocommit=False, expire_on_commit=True)

# 创建基本的映射类
Base = declarative_base(bind=engin, name='Base')