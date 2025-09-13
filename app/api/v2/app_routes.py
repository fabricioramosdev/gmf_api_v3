from fastapi import APIRouter, Depends, HTTPException
from typing import List

from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.app_version_old import AppVersionCreate, AppVersionResponse
from app.db.crud import create_app_version, get_latest_app_version, get_all_app_versions

router = APIRouter()

@router.post("/app-version/", response_model=AppVersionResponse)
def set_app_version(payload: AppVersionCreate, db: Session = Depends(get_db)):
    return create_app_version(db=db, version=payload.version, platform=payload.platform)

@router.get("/app-version/latest/{platform}", response_model=AppVersionResponse)
def get_latest_version(platform: str, db: Session = Depends(get_db)):
    version = get_latest_app_version(db, platform)
    if not version:
        raise HTTPException(status_code=404, detail="Versão não encontrada")
    return version

@router.get("/app-version/all", response_model=List[AppVersionResponse])
def list_versions(db: Session = Depends(get_db)):
    return get_all_app_versions(db)
