# ============================================================
# routers/checklists_items_inspected.py
# ============================================================
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.db.models import (
                           Checklist, 
                           UploadFile, 
                           ChecklistItemsInspected
                           ) 

from app.schemas.dtos import (
    ChecklistItemCreate,
    ChecklistItemUpdate,
    ChecklistItemOut,
)

router = APIRouter(prefix="/checklists", tags=["Checklist • Itens Inspecionados"])


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def _ensure_checklist_exists(db: Session, checklist_id: int) -> Checklist:
    checklist = db.get(Checklist, checklist_id)
    if not checklist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Checklist {checklist_id} não encontrado",
        )
    return checklist


def _ensure_photo_exists(db: Session, photo_id: int) -> UploadFile:
    photo = db.get(UploadFile, photo_id)
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Foto (upload_files) {photo_id} não encontrada",
        )
    return photo


def _get_item_row(
    db: Session, checklist_id: int, item_id: int
) -> Optional[ChecklistItemsInspected]:
    stmt = (
        select(ChecklistItemsInspected)
        .where(ChecklistItemsInspected.fk_checklist == checklist_id)
        .where(ChecklistItemsInspected.fk_item == item_id)
    )
    return db.execute(stmt).scalars().first()


# ============================================================
# GET /v3/checklists/{checklist_id}/items
# ============================================================
@router.get("/{checklist_id}/items", response_model=List[ChecklistItemOut])
def list_items_for_checklist(
    checklist_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _ensure_checklist_exists(db, checklist_id)

    stmt = (
        select(ChecklistItemsInspected)
        .where(ChecklistItemsInspected.fk_checklist == checklist_id)
        .order_by(ChecklistItemsInspected.id.asc())
    )
    return db.execute(stmt).scalars().all()


# ============================================================
# POST /v3/checklists/{checklist_id}/items
# Cria 1 item (estilo curl)
# ============================================================
@router.post(
    "/{checklist_id}/items",
    response_model=ChecklistItemOut,
    status_code=status.HTTP_201_CREATED,
)
def create_item_for_checklist(
    checklist_id: int,
    payload: ChecklistItemCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _ensure_checklist_exists(db, checklist_id)

    # Regra de consistência: não pode duplicar o mesmo item no mesmo checklist
    existing = _get_item_row(db, checklist_id, payload.item_id)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Item já existe neste checklist. Use PATCH para atualizar.",
        )

    # Se você permitir já mandar photo_id (mesmo que a ideia seja mandar depois), valida aqui
    if getattr(payload, "photo_id", None) is not None:
        _ensure_photo_exists(db, payload.photo_id)

    row = ChecklistItemsInspected(
        fk_checklist=checklist_id,
        fk_item=payload.item_id,
        status=payload.status,
        # ✅ novo fluxo: chega o nome agora
        photo_name=getattr(payload, "photo_name", None),
        # ✅ id pode vir agora (se você quiser) ou depois no PATCH
        fk_photo=getattr(payload, "photo_id", None),
    )

    db.add(row)
    db.commit()
    db.refresh(row)
    return row


# ============================================================
# PATCH /v3/checklists/{checklist_id}/items/{item_id}
# Atualiza status e/ou cola photo_id depois
# ============================================================
@router.patch("/{checklist_id}/items/{item_id}", response_model=ChecklistItemOut)
def update_single_item(
    checklist_id: int,
    item_id: int,
    payload: ChecklistItemUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _ensure_checklist_exists(db, checklist_id)

    row = _get_item_row(db, checklist_id, item_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item inspecionado não encontrado para este checklist",
        )

    # valida photo_id se vier
    if payload.photo_id is not None:
        _ensure_photo_exists(db, payload.photo_id)

    # atualiza status (se veio)
    if payload.status is not None:
        row.status = payload.status

    # atualiza photo_name (se veio)
    if hasattr(payload, "photo_name") and payload.photo_name is not None:
        row.photo_name = payload.photo_name

    # atualiza fk_photo somente se o campo veio no payload (mesmo None)
    if "photo_id" in payload.model_fields_set:
        row.fk_photo = payload.photo_id

    db.add(row)
    db.commit()
    db.refresh(row)
    return row


# ============================================================
# DELETE /v3/checklists/{checklist_id}/items/{item_id}
# ============================================================
@router.delete("/{checklist_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_single_item(
    checklist_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _ensure_checklist_exists(db, checklist_id)

    row = _get_item_row(db, checklist_id, item_id)
    if row is None:
        return  # idempotente

    db.delete(row)
    db.commit()
    return