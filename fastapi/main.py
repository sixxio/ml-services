# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import crud
import models
from datetime import datetime, timedelta
import jwt
from typing import Annotated

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

SECRET_KEY = "2409832094810948219048120948120941309483209482304802394829304820934802938409234803924"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id: int = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    return user_id

@app.post("/sign-up/", response_model=models.UserModel)
def sign_up(user: models.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)


@app.post("/token")
def sign_in(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, form_data.username)
    if user is None or not crud.verify_password(form_data.password, user.hash):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": str(user.id), "exp": expires}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": encoded_jwt, "token_type": "bearer", "user_id":user.id}


@app.post("/users/", response_model=models.UserModel, current_user: str = Depends(get_current_user))
def create_user(user: models.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)

@app.get("/users/{user_id}", response_model=models.UserModel, current_user: str = Depends(get_current_user))
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.get("/models/", response_model=list[models.ModelModel], current_user: str = Depends(get_current_user))
def read_models(db: Session = Depends(get_db)):
    return crud.read_models(db)

@app.post("/models/", response_model=models.ModelModel)
def create_model(model: models.ModelCreate, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    return crud.create_model(db, model)

@app.post("/transactions/", response_model=models.TransactionModel)
def create_transaction(transaction: models.TransactionCreate, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    return crud.create_transaction(db, transaction)

@app.get("/transactions/{user_id}", response_model=list[models.TransactionModel])
def read_transactions_for_user(user_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    return crud.read_transactions_for_user(db, user_id)

@app.post("/predictions/", response_model=models.PredictionModel)
def create_prediction(prediction: models.PredictionCreate, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    return crud.create_prediction(db, prediction)

@app.get("/predictions/{user_id}", response_model=list[models.PredictionModel])
def read_predictions_for_user(user_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    return crud.read_predictions_for_user(db, user_id)

