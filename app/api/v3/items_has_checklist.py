# app/api/v2/checklist_items_routes.py
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Path, status, Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.db.models import User, Checklist
from app.db.crud import (
    get_checklist_item,
    add_item_to_checklist,
    update_checklist_item,
    delete_checklist_item,
    bulk_add_items,
    set_item_photo
)
from app.schemas.dtos import (
    ChecklistItemCreate, ChecklistItemUpdate, ChecklistItemOut, ChecklistItemsBulkCreate
)

router = APIRouter(prefix="/checklists/{checklist_id}/items", tags=["Checklist >> Items inspected" ])

def _is_admin(u: User) -> bool:
    return getattr(u, "is_admin", False) or str(getattr(u, "role", "")).lower() == "admin"

def _can_touch_checklist(db: Session, checklist_id: int, current_user: User) -> Checklist:
    obj = db.get(Checklist, checklist_id)
    if not obj:
        raise HTTPException(404, "Checklist não encontrado.")
    if not _is_admin(current_user) and obj.fk_user != current_user.id:
        raise HTTPException(403, "Permissão negada.")
    return obj

@router.post("", response_model=ChecklistItemOut, status_code=status.HTTP_201_CREATED)
def create_item(
    checklist_id: int = Path(..., ge=1),
    payload: ChecklistItemCreate = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    
    def _norm_photo_id(v):
        if v in (None, "", 0, "0", False):  # trate 0/“0”/vazio como sem foto
            return None
        try:
            iv = int(v)
            return iv if iv > 0 else None
        except Exception:
            return None


    _can_touch_checklist(db, checklist_id, current_user)
    # tenta criar; se já existe, devolve 409
    exists = get_checklist_item(db, checklist_id, payload.item_id)
    if exists:
        raise HTTPException(409, "Item já vinculado a este checklist.")
    obj = add_item_to_checklist(
        db,
        checklist_id=checklist_id,
        item_id=payload.item_id,
        status=payload.status,
        photo_id=payload.photo_id,
    )

    # ✅ normaliza photo_id: só usa se for inteiro > 0
    photo_id = _norm_photo_id(payload.photo_id)

    # (opcional) garantir unicidade da foto: não deixar mesma foto em outro item
    if photo_id is not None:
        set_item_photo(db, checklist_id=checklist_id, item_id=payload.item_id, photo_id=payload.photo_id)
    
    return obj

@router.put("/{item_id}", response_model=ChecklistItemOut)
def update_item(
    checklist_id: int = Path(..., ge=1),
    item_id: int = Path(..., ge=1),
    payload: ChecklistItemUpdate = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _can_touch_checklist(db, checklist_id, current_user)
    data = payload.model_dump(exclude_unset=True)
    obj = update_checklist_item(db, checklist_id=checklist_id, item_id=item_id, data=data)
    if not obj:
        raise HTTPException(404, "Vínculo item↔checklist não encontrado.")
    return obj

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    checklist_id: int = Path(..., ge=1),
    item_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _can_touch_checklist(db, checklist_id, current_user)
    ok = delete_checklist_item(db, checklist_id=checklist_id, item_id=item_id)
    if not ok:
        raise HTTPException(404, "Vínculo item↔checklist não encontrado.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/bulk", response_model=list[ChecklistItemOut], status_code=status.HTTP_201_CREATED)
def bulk_create_items(
    checklist_id: int = Path(..., ge=1),
    payload: ChecklistItemsBulkCreate = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _can_touch_checklist(db, checklist_id, current_user)
    items = [it.model_dump() for it in payload.items]
    objs = bulk_add_items(db, checklist_id=checklist_id, items=items, upsert=True)
    return objs
