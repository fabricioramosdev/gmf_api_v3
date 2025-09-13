from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.core.dependencies import  get_current_user
from app.db.models import User

from app.schemas.dtos import (EmergencyCreate, EmergencyOut)

from app.db.crud import (create_emergency_request, get_emergency_requests,
                        get_emergency_request_by_id, verify_emergency_request)


router = APIRouter(prefix="/sos", tags=["S.O.S"])

@router.post("/", response_model=EmergencyOut)
def create_emergency(
    payload: EmergencyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_emergency_request(
        db=db,
        user_id=current_user.id,
        lat=payload.lat,
        long=payload.long
    )


@router.get("/", response_model=List[EmergencyOut])
def list_emergency_requests(db: Session = Depends(get_db)):
    return get_emergency_requests(db)


@router.put("/{request_id}/to_check", response_model=EmergencyOut)
def to_check_emergency(request_id: int, db: Session = Depends(get_db)):
    request = get_emergency_request_by_id(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Solicitação de emergência não encontrada")
    return verify_emergency_request(db, request)
