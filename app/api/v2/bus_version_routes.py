from fastapi import APIRouter, Depends, HTTPException
from app.db.session import get_db
from typing import List
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.db.models import User
from app.schemas.bus_version_old import BusVersionCreate, BusVersionResponse
from app.db.crud import create_bus_version, get_all_bus_versions, get_bus_version_by_id, delete_bus_version

router = APIRouter()

@router.post("/bus-versions/", response_model=BusVersionResponse)
def create_bus_version_route(
    payload: BusVersionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_bus_version(db=db, nome=payload.nome)

@router.get("/bus-versions/", response_model=List[BusVersionResponse])
def list_bus_versions(db: Session = Depends(get_db)):
    return get_all_bus_versions(db)

@router.delete("/bus-versions/{version_id}", response_model=dict)
def delete_bus_version_route(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    version = get_bus_version_by_id(db, version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Versão de ônibus não encontrada")
    delete_bus_version(db, version)
    return {"message": "Versão removida com sucesso"}
