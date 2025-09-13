from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.db.models import User

from app.schemas.emergency_request_old import (EmergencyRequestCreate, 
                                           EmergencyRequestResponse)

from app.db.crud import (create_emergency_request,
                        get_emergency_requests,
                        get_emergency_request_by_id,
                        verify_emergency_request)

router = APIRouter()

@router.post("/emergency/", response_model=EmergencyRequestResponse)
def create_emergency(
    payload: EmergencyRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_emergency_request(
        db=db,
        user_id=current_user.id,
        latitude=payload.latitude,
        longitude=payload.longitude
    )

@router.get("/emergency/", response_model=List[EmergencyRequestResponse])
def list_emergency_requests(db: Session = Depends(get_db)):
    return get_emergency_requests(db)

@router.put("/emergency/{request_id}/verify", response_model=EmergencyRequestResponse)
def verify_emergency(request_id: int, db: Session = Depends(get_db)):
    request = get_emergency_request_by_id(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Solicitação de emergência não encontrada")
    return verify_emergency_request(db, request)
