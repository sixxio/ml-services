# models.py
from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict

class UserBase(BaseModel):
    email: str
    name: str
    login: str
    balance: float

class UserCreate(UserBase):
    hash: str

class UserModel(UserBase):
    id: int
    created_at: datetime


class ModelBase(BaseModel):
    name: str
    description: str
    path_to_dump: str
    cost: float

class ModelCreate(ModelBase):
    pass

class ModelModel(ModelBase):
    id: int
    created_at: datetime


class TransactionBase(BaseModel):
    amount: float
    user_id: int

class TransactionCreate(TransactionBase):
    pass

class TransactionModel(TransactionBase):
    id: int
    created_at: datetime


class PredictionBase(BaseModel):
    model_id: int
    user_id: int
    input_data: str
    output_data: str

class PredictionCreate(PredictionBase):
    pass

class PredictionModel(PredictionBase):
    id: int
    created_at: datetime

