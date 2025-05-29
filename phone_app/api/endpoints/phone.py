from phone_app.db.models import Phone
from phone_app.db.schema import PhoneSchema
from sqlalchemy.orm import Session
from phone_app.db.database import SessionLocal
from fastapi import Depends, HTTPException, APIRouter
from typing import List, Optional
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

phone_router = APIRouter(prefix='/phone',  tags=['Phone'])

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

model_path = BASE_DIR / 'phone_price_model_job.pkl'
scaler_path = BASE_DIR / 'scaler.pkl'

model = joblib.load(model_path)
scaler = joblib.load(scaler_path)


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@phone_router.post('/', response_model=PhoneSchema, summary='Создать phone')
async def create_phone(phone: PhoneSchema, db: Session = Depends(get_db)):
    phone_db = Phone(phone_name=phone.id)
    db.add(phone_db)
    db.commit()
    db.refresh(phone_db)
    return phone_db


@phone_router.get('/', response_model=List[PhoneSchema], summary='Получить все phone')
async def phone_list(db: Session = Depends(get_db)):
    return db.query(Phone).all()


@phone_router.get('/{phone_id}', response_model=PhoneSchema, summary='Получить phone')
async def phone_detail(phone_id: int, db: Session = Depends(get_db)):
    phone = db.query(Phone).filter(Phone.id == phone_id).first()

    if phone is None:
        raise HTTPException(status_code=400, detail='Мындай маалымат жок')
    return phone


@phone_router.put('/{phone_id}', summary='Обновить phone')
async def phone_update(phone_id: int, phone: PhoneSchema, db: Session = Depends(get_db)):
    phone_db = db.query(Phone).filter(Phone.id == phone_id).first()

    if phone_db is None:
        raise HTTPException(status_code=400, detail='Мындай маалымат жок')

    for phone_key, phone_values in phone.dict().items():
        setattr(phone_db, phone_key, phone_values)

    phone_db.id = phone.id
    db.add(phone_db)
    db.commit()
    db.refresh(phone_db)
    return phone_db


@phone_router.delete('/{phone_id}', summary='Удалить')
async def phone_delete(phone_id: int, db: Session = Depends(get_db)):
    phone_db = db.query(Phone).filter(Phone.id == phone_id).first()

    if phone_db is None:
        raise HTTPException(status_code=400, detail='Мындай маалымат жок')

    db.delete(phone_db)
    db.commit()
    db.refresh()
    return {'message': 'This phone is deleted'}

model_columns = [
    'Rating',
    'Num_Ratings',
    'RAM',
    'ROM',
    'Battery',
    'Front_Cam',
]


@phone_router.post('/predict')
async def predict_price(predict: PhoneSchema, db: Session = Depends(get_db)):
    input_data = {
        'Rating': predict.rating,
        'Num_Ratings': predict.num_ratings,
        'RAM': predict.ram,
        'ROM': predict.rom,
        'Battery': predict.battery,
        'Front_Cam': predict.front_cam
    }
    input_df = pd.DataFrame([input_data])
    scaled_df = scaler.transform(input_df)
    predicted_price = model.predict(scaled_df)[0]
    return {'predicted_price': round(predicted_price)}