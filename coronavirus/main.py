# !/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = "Teng"

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from coronavirus import crud, schemas
from coronavirus.database import engin, Base, SessionLocal
from coronavirus.models import City, Data
from fastapi.templating import Jinja2Templates

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

#前后端不分离的接口，使用模板引擎
@application.get("/")
def coronavirus(request: Request, city: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    data = crud.get_data(db=db, city=city, skip=skip, limit=limit)
    return templates.TemplateResponse("home.html", {
        "request": request,
        "data": data,
        "sync_data_url": "/sync_coronavirus_data/jhu"
    })
