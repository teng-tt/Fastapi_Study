# !/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = "Teng"

import requests
from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from sqlalchemy.orm import Session
from coronavirus import crud, schemas
from coronavirus.database import engin, Base, SessionLocal
from coronavirus.models import City, Data
from fastapi.templating import Jinja2Templates
from pydantic import HttpUrl

application = APIRouter()
templates = Jinja2Templates(directory="./coronavirus/templates")

Base.metadata.create_all(bind=engin)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@application.post("/create_city", response_model=schemas.ReadCity)
def create_city(city: schemas.CreateCity, db: Session = Depends(get_db)):
    db_city = crud.get_city_by_name(db=db, city=city.province)
    if db_city:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="City already registered"
        )
    return crud.create_city(db=db , city=city)


@application.get("/get_city/{city}", response_model=schemas.ReadCity)
def get_city(city: str, db: Session = Depends(get_db)):
    db_city = crud.get_city_by_name(db=db, city=city)
    if db_city is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="City not found"
        )
    return db_city

@application.get("get_cities")
def get_cities(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    cities = crud.get_cities(db=db, skip=skip, limit=limit)
    return cities

@application.post("/create_data", response_model=schemas.ReadData)
def create_date_for_city(city: str, data: schemas.CreateData, db: Session = Depends(get_db)):
    db_city = crud.get_city_by_name(db=db, city=city)
    data = crud.create_city_data(db=db, data=data, city_id=db_city.id)
    return data

@application.get("/get_data")
def get_data(city: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    data = crud.get_data(db=db, city=city, skip=skip, limit=limit)
    return data


def bg_task(url: HttpUrl, db: Session):
    """ 这里注意一个坑，不要在后台任务的参数汇总db: Session = Depends(get_db)这样导入依赖 """
    city_data = requests.get(url=f"{url}?source=jhu&country_code=CN&timelines=false")

    if 200 == city_data.status_code:
        db.query(City).delete()
        for localtion in city_data.json()["locations"]:
            city = {
                "province": localtion["province"],
                "country": localtion["country"],
                "country_code": "CN",
                "country_population": localtion["country_population"],
            }
            crud.create_city(db=db, city=schemas.CreateCity(**city))

    coronavirus_data = requests.get(url=f"{url}?source=jhu&country_code=CN&timelines=true")

    if 200 == coronavirus_data.status_code:
        db.query(Data).delete()
        for city in coronavirus_data.json()["locations"]:
            db_city = crud.get_city_by_name(db=db, city=city["province"])
            for data, confirmed in city["timelines"]["confirmed"]["timeline"].items():
                data = {
                    "date": data.split("T")[0],  # 把'2020-12-31T00:00:00Z' 变为 '2020-12-31'
                    "confirmed": confirmed,
                    "deaths": city["timelines"]["deaths"]["timeline"][data],
                    "recovered": 0 #每个城市每天有多少人痊愈，这种数据没有
                }
                crud.create_city_data(db=db, data=schemas.CreateData(**data), city_id=db_city.id)

@application.get("/sync_coronavirus_data/jhu")
def sync_coronavirus_data(background_task: BackgroundTasks, db: Session = Depends(get_db)):
    """ 从Johns Hopkins University同步COVID-19数据 """
    background_task.add_task(bg_task, "http://coronavirus-tracker-api.herokuapp.com/v2/locations", db)
    return {"message": "正在同步数据......"}


#前后端不分离的接口，使用模板引擎
@application.get("/")
def coronavirus(request: Request, city: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    data = crud.get_data(db=db, city=city, skip=skip, limit=limit)
    return templates.TemplateResponse("home.html", {
        "request": request,
        "data": data,
        "sync_data_url": "/coronavirus/sync_coronavirus_data/jhu"
    })

