# !/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = "Teng"


import uvicorn
import time
from fastapi import FastAPI, Request
from fastapistudy import app03, app04, app05, app06, app07, app08
from fastapi.staticfiles import StaticFiles
from coronavirus import application
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.exceptions import RequestValidationError
# from fastapi.responses import PlainTextResponse
# from fastapi.exceptions import HTTPException

app = FastAPI(
    title="FastApi Study and Coronavirus Tracker API Docs",
    description='FastApi 学习 新冠病毒疫情跟踪器API接口文档',
    version='1.0.0',
    docs_url='/docs',
    redoc_url='/redoc'
)

# mount表示将某个目录下一个完全独立的应用挂载过来，这个不会在api交互文档中显示
# 挂载静态目录，模板css等文件
app.mount(path='/static', app=StaticFiles(directory='E:/python-daimaxuexi/fastapi_study/coronavirus/static'), name='static')

# @app.exception_handler(HTTPException)  #重写HTTPException异常处理器
# async def http_exception_handler(request, exc):
#     '''
#     :param request: 这个参数不能省
#     :param exc:
#     :return:
#     '''
#     return PlainTextResponse(str(exc.detail), status_code=exc.status_code)
#
# @app.exception_handler((RequestValidationError))  #重写请求验证异常处理器
# async def validation_exception_handler(request, exc):
#     '''
#     :param request: 这个参数不能省
#     :param exc:
#     :return:
#     '''
#     return PlainTextResponse(str(exc.detail), status_code=400)


@app.middleware('http')
async def add_process_time_header(request: Request, call_next):  # call_next将接收request请求值为参数
    start_time = time.time()
    response = await call_next(request)
    processtime = time.time() - start_time
    response.headers['X-Process-Time'] = str(processtime) # 添加自定义的以X-开头的请求头
    return response


# CORS 允许跨域共享
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1",
        "http://127.0.0.1:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(app03, prefix='/chapter03', tags=['第三章 请求参数和验证'])
app.include_router(app04, prefix='/chapter04', tags=['第四章 响应处理和FastAPI配置'])
app.include_router(app05, prefix='/chapter05', tags=['第五章 FastAPI的依赖注入系统'])
app.include_router(app06, prefix='/chapter06', tags=['第六章 安全认证和授权'])
app.include_router(app07, prefix='/chapter07', tags=['第七章 数据库操作多目录结构设计'])
app.include_router(app08, prefix='/chapter08', tags=['第八章 中间件 CORS 后台任务 测试用例'])
app.include_router(application, prefix='/coronavirus', tags=['新冠疫情病情追踪器api'])

if __name__ == '__main__':
    '''
        启动app
    '''
    uvicorn.run('run:app', host='0.0.0.0', port=8000, reload=True, debug=True, workers=1)
