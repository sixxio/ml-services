# crud.py
from sqlalchemy.orm import Session
from models import UserCreate, ModelCreate, TransactionCreate, PredictionCreate
from database import User, Model, Transaction, Prediction
import json, pandas as pd, joblib

def create_user(db: Session, user: UserCreate):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def verify_password(plain_password: str, hashed_password: str):
    return plain_password == hashed_password

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def create_model(db: Session, model: ModelCreate):
    db_model = Model(**model.dict())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model

def read_models(db: Session):
    return db.query(Model).all()

def create_transaction(db: Session, transaction: TransactionCreate):
    db_transaction = Transaction(**transaction.dict())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    user = db.query(User).filter(User.id == transaction.user_id).first()
    if user:
        user.balance += transaction.amount
        db.commit()
        db.refresh(user)
    return db_transaction

def read_transactions_for_user(db: Session, user_id: int):
    return db.query(Transaction).filter(Transaction.user_id == user_id).all()

def create_prediction(db: Session, prediction: PredictionCreate):
    db_prediction = Prediction(**prediction.model_dump())
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    user = db.query(User).filter(User.id == prediction.user_id).first()
    if user:
        data = pd.DataFrame(json.loads(prediction.input_data))
        model = db.query(Model).filter(Model.id == prediction.model_id).first()
        user.balance -= data.shape[0]*model.cost
        model = joblib.load(model.path_to_dump)
        db_prediction.output_data = pd.DataFrame(model.predict(data)).to_json()
        db.commit()
        db.refresh(user)
    return db_prediction

def read_predictions_for_user(db: Session, user_id: int):
    return db.query(Prediction).filter(Prediction.user_id == user_id).all()
