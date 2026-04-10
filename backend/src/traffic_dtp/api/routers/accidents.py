from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.traffic_dtp.db.session import SessionLocal
from src.traffic_dtp.db.models.accident import Accident
from src.traffic_dtp.db.schemas.accident import AccidentResponse

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/accidents/", response_model=list[AccidentResponse])
def get_accidents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    accidents = db.query(Accident).offset(skip).limit(limit).all()
    return accidents

@router.get("/accidents/{accident_id}", response_model=AccidentResponse)
def get_accident(accident_id: int, db: Session = Depends(get_db)):
    accident = db.query(Accident).filter(Accident.id == accident_id).first()
    if not accident:
        raise HTTPException(status_code=404, detail="ДТП не найдено")
    return accident