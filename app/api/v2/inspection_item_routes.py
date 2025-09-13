from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.services.audit_service import log_action

from app.db.models import User
from app.schemas.inspection_item import InspectionItemCreate, InspectionItemResponse
from app.db.crud import (
    create_inspection_item,
    get_all_inspection_items,
    get_inspection_item_by_id,
    delete_inspection_item,
    update_inspection_item
)

router = APIRouter()

@router.post("/inspection-items/", response_model=InspectionItemResponse)
def create_inspection_items(item: InspectionItemCreate, 
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    log_action(
        action="create inspection-items",
        previous_data={},
        current_data=item.model_dump(),
        db=db,
        current_user=current_user
    )
    return create_inspection_item(db, nome=item.nome, status=item.status, obrigatorio=item.obrigatorio)


@router.delete("/inspection-items/{item_id}")
def delete_inspection_items(item_id: int,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    item = get_inspection_item_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")

    log_action(
        action="delete inspection-items",
        previous_data={
            "id": item.id,
            "nome": item.nome,
            "status": item.status,
            "obrigatorio": item.obrigatorio
        },
        current_data={},
        db=db,
        current_user=current_user
    )

    delete_inspection_item(db, item)
    return {"message": "Item removido com sucesso"}


@router.put("/inspection-items/{item_id}", response_model=InspectionItemResponse)
def update_inspection_items(item_id: int,
                item: InspectionItemCreate,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    db_item = get_inspection_item_by_id(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item não encontrado")

    previous_data = {
        "id": db_item.id,
        "nome": db_item.nome,
        "status": db_item.status,
        "obrigatorio": db_item.obrigatorio
    }

    updated_item = update_inspection_item(
        db,
        db_item,
        updates={
            "nome": item.nome,
            "status": item.status,
            "obrigatorio": item.obrigatorio
        }
    )

    log_action(
        action="update inspection-items",
        previous_data=previous_data,
        current_data=item.model_dump(),
        db=db,
        current_user=current_user
    )

    return updated_item


@router.get("/inspection-items/", response_model=List[InspectionItemResponse])
def list_items(db: Session = Depends(get_db)):
    return get_all_inspection_items(db)
