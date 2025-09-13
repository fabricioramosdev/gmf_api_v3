from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.db.models import User, Checklist
from app.core.dependencies import get_current_user
from app.services.audit_service import log_action


from app.schemas.dtos import (
    ChecklistCreate, ChecklistUpdate, 
    ChecklistOut
)

from app.db.crud import (
    get_checklist_by_id, list_all_checklists
)

CHECKLIST_STATUS_CODE_TO_DB = {
    1: "INICIADO",
    2: "EM_TRANSPORTE",
    3: "ENTREGUE",
    4: "CONCLUIDO",
}

router = APIRouter(prefix="/check-list", tags=["Checklists"])

@router.post("/", response_model=ChecklistOut, status_code=201)
def create_checklist(payload: ChecklistCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = Checklist(
        fk_cliente = payload.fk_cliente,
        fk_user    = current_user.id,
        version_bus= payload.version_bus,
        km_start   = payload.km_start,
        fuel_start = payload.fuel_start,
        obs        = payload.obs,
        status     = CHECKLIST_STATUS_CODE_TO_DB[payload.status_code], 
    )
    db.add(obj); db.commit(); db.refresh(obj)
    return obj


@router.put("/{checklist_id}", response_model=ChecklistOut)
def update_checklist(checklist_id: int, payload: ChecklistUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = db.get(Checklist, checklist_id)
    if not obj: raise HTTPException(404, "Checklist não encontrado.")
    data = payload.model_dump(exclude_unset=True)
    if "status_code" in data and data["status_code"] is not None:
        obj.status = CHECKLIST_STATUS_CODE_TO_DB[data.pop("status_code")] 
    for k, v in data.items(): setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return obj


@router.get("/checklists/{checklist_id}", response_model=ChecklistOut)
def get_checklist_detail(
    checklist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    checklist = get_checklist_by_id(db=db, checklist_id=checklist_id)
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist não encontrado.")
    
    # ✅ Admin pode ver qualquer checklist
    is_admin = (
        getattr(current_user, "is_admin", False)
        or str(getattr(current_user, "role", "")).lower() == "admin"
    )

    if not is_admin and checklist.fk_user != current_user.id:
        raise HTTPException(status_code=403, detail="Permissão negada.")

    return checklist


@router.get("/checklists/", response_model=List[ChecklistOut])
def list_user_checklists(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    checklists = list_all_checklists(db=db, user_id=current_user.id)
    return checklists



