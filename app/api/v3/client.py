from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List


from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.services.audit_service import log_action
from app.db.models import  User

from app.schemas.dtos import (
    ClientCreate, ClientOut,
)
from app.db.crud import (create_client, get_all_clients, 
                         get_client_by_id, update_client, delete_client)



router = APIRouter(prefix="/client", tags=["Client"])


@router.post("/", response_model=ClientOut)
def create_clients(client: ClientCreate,
                    db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
  
    log_action(
        action="create clients",
        previous_data={},
        current_data=client.model_dump(),
        db=db,
        current_user=current_user
    )
    return create_client(db, name=client.name, mail=client.mail, phone=client.phone)




@router.get("/", response_model=List[ClientOut])
def list_clients(db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    """
    Retorna uma lista de todos os clientes registrados no banco de dados.
    """
    return get_all_clients(db)



@router.put("/{client_id}", response_model=ClientOut)
def update_clients(
    client_id: int,
    client: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_client = get_client_by_id(db, client_id)
    if not db_client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    previous_data = {
        "name": db_client.name,
        "mail": db_client.mail
    }

    updated_client = update_client(db, db_client, {
        "name": client.name,
        "mail": client.mail
    })

    log_action(
        action="update client",
        previous_data=previous_data,
        current_data=client.model_dump(),
        db=db,
        current_user=current_user
    )

    return updated_client


@router.delete("/clients/{client_id}")
def delete_clients(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_client = get_client_by_id(db, client_id)
    if not db_client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    previous_data = {
        "name": db_client.name,
        "mail": db_client.mail
    }

    delete_client(db, db_client)

    log_action(
        action="delete client",
        previous_data=previous_data,
        current_data={},
        db=db,
        current_user=current_user
    )

    return {"message": "Cliente removido com sucesso."}
