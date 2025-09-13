from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.db.models import User
from app.core.dependencies import get_current_user
from app.schemas.checklist_old import (
    ChecklistCreate, ChecklistResponse, 
    ChecklistInspectedCreate, ItemFotoAssociationRequest
)
from app.db.crud import (
    create_checklist, get_checklist_by_id, list_all_checklists,
      add_inspected_items, associate_photos_to_inspected_items
)

router = APIRouter()


# 1. Criar o checklist base (sem itens nem uploads)
@router.post("/checklists/", response_model=ChecklistResponse)
def create_checklist_base(
    checklist: ChecklistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:

        checklist = create_checklist(db=db, checklist=checklist, user_id=current_user.id)
        return checklist
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar checklist: {str(e)}")


# 2. Adicionar itens inspecionados posteriormente
@router.post("/checklists/{checklist_id}/itens")
def add_checklist_inspected_items(
    checklist_id: int,
    itens: List[ChecklistInspectedCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    checklist = get_checklist_by_id(db, checklist_id=checklist_id)
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist não encontrado.")

    if checklist.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Permissão negada.")

    return  add_inspected_items(db=db, checklist_id=checklist_id, itens=itens)



# 3. Consultar checklist com detalhes
@router.get("/checklists/{checklist_id}", response_model=ChecklistResponse)
def get_checklist_detail(
    checklist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    checklist = get_checklist_by_id(db=db, checklist_id=checklist_id)

    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist não encontrado.")
    
    if checklist.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Permissão negada.")

    return checklist


# 4. Listar todos os checklists do usuário
@router.get("/checklists/", response_model=List[ChecklistResponse])
def list_user_checklists(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    checklists = list_all_checklists(db=db, user_id=current_user.id)
    return checklists



@router.post("/checklists/associar-fotos")
def associate_photos(
    associations_request: ItemFotoAssociationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        associate_photos_to_inspected_items(
            db=db, 
            associations=[assoc.dict() for assoc in associations_request.associations]
        )
        return {"message": "Fotos associadas aos itens inspecionados com sucesso."}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao associar fotos: {str(e)}")