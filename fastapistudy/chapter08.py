# !/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = "Teng"

from typing import Optional
from fastapi import APIRouter,BackgroundTasks, Depends

app08 = APIRouter()


''' 见run.py middleware 中间件 '''
# 注意 带yiled的依赖的退出部分代码 和后台任务 会在中间件之后运行

''' 见run.py CORS 跨域资源共享'''
# 域的概念： 协议+域名+端口

''' 后台任务 '''

def bg_task(framework: str):
    with open("README.md", mode="a") as f:
        f.write(f"## {framework} 框架学习")

@app08.post("/background_tasks")
async def run_bg_task(framework: str, background_task: BackgroundTasks):
    """
    :param framework: 别调用的后台任务函数的参数
    :param background_task: FastApi.BackgroundTasks
    :return:
    """
    background_task.add_task(func=bg_task, framework=framework)
    return {"message": "任务已在后台运行"}


def continue_write_readme(background_tasks: BackgroundTasks, q: Optional[str] = None ):
    if q:
        background_tasks.add_task(bg_task, ">\n 整体学习FastApi框架\n ")
    return q


@app08.post("/dependency/background_tasks")
async def dependency_run_bg_task(q: str = Depends(continue_write_readme)):
    if q:
        return {"message": "README.md更新成功"}
