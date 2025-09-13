#app\api\v2\client_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List


from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.services.audit_service import log_action
from app.db.models import  User
from app.schemas.client import (
    ClientCreate, ClientResponse,
)
from app.db.crud import (create_client, get_all_clients,get_client_by_id, update_client, delete_client)


# Cria um roteador FastAPI para as rotas de clientes
router = APIRouter()

# --- CLIENTES ---

# Rota para criar um novo cliente
@router.post("/clients/", response_model=ClientResponse)
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
    return create_client(db, nome=client.nome, email=client.email)

# Rota para listar todos os clientes cadastrados
@router.get("/clients/", response_model=List[ClientResponse])
def list_clients(db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    """
    Retorna uma lista de todos os clientes registrados no banco de dados.
    """
    return get_all_clients(db)


@router.put("/clients/{client_id}", response_model=ClientResponse)
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
        "nome": db_client.nome,
        "email": db_client.email
    }

    updated_client = update_client(db, db_client, {
        "nome": client.nome,
        "email": client.email
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
        "nome": db_client.nome,
        "email": db_client.email
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
