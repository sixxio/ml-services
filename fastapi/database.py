# database.py
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

# SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:postgres@postgres:5432/postgres'
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    login = Column(String)
    hash = Column(String)
    balance = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    transactions = relationship("Transaction", back_populates="user")
    predictions = relationship("Prediction", back_populates="user")

class Model(Base):
    __tablename__ = "models"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    cost = Column(Float)
    path_to_dump = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    predictions = relationship("Prediction", back_populates="model")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="transactions")


class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    input_data = Column(JSON)
    output_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="predictions")

    model_id = Column(Integer, ForeignKey("models.id"))
    model = relationship("Model", back_populates="predictions")

Base.metadata.create_all(bind=engine)

db = SessionLocal()
gbc = Model(id = 1,
            name = "GBC",
            description = "Gradient Boosting Classifier",
            cost = 5,
            path_to_dump = "./models/GradientBoostingClassifier.joblib",
            created_at = str(datetime.now()))
rfc = Model(id = 2,
            name = "RFC",
            description = "Random Forest Classifier",
            cost = 10,
            path_to_dump = "./models/RandomForestClassifier.joblib",
            created_at = str(datetime.now()))
xgbc = Model(id = 3,
            name = "XGBC",
            description = "XGB Classifier",
            cost = 15,
            path_to_dump = "./models/XGBClassifier.joblib",
            created_at = str(datetime.now()))

db.add(gbc)
db.add(rfc)
db.add(xgbc)

db.commit()
