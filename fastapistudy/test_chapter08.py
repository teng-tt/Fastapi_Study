# !/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = "Teng"

from fastapi.testclient import TestClient
from run import app

""" 测试用例 """

client = TestClient(app)  # 先安装pytest

def test_run_bg_task(): # 主义不是async def  h函数test开头是一种pytest规范
    response = client.post(url="/chapter08/background_tasks?framework=FastApi")
    assert response.status_code == 200
    assert response.json() == {"message": "任务已在后台运行"}


def test_dependency_run_bg_task():
    response = client.post(url="/chapter08/dependency/background_tasks")
    assert response.status_code == 200
    assert response.json() is None


def test_dependency_run_bg_task_q():
    response = client.post(url="/chapter08/dependency/background_tasks?q=1")
    assert response.status_code == 200
    assert response.json() == {"message": "README.md更新成功"}