#user_routes.py
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session
from sqlalchemy import func


from datetime import datetime

from app.db.session import get_db
from app.db.models import Checklist, User
from app.db.crud import (
    create_user, get_user, update_user, delete_user, change_password
)
from app.schemas.user import UserCreate, UserUpdate, PasswordChange, UserResponse
from app.core.dependencies import get_current_user

router = APIRouter()


@router.post("/users/", response_model=UserResponse)
def create(user_data: UserCreate, db: Session = Depends(get_db)):
    if get_user(db, user_data.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Usuário já existe")
    
    return create_user(
                        db,
                        email=user_data.email,
                        password=user_data.password,
                        **user_data.dict(exclude={"password", "email"})
                    )


@router.get("/users/me", response_model=UserResponse)
def get_logged_in_user(current_user: User = Depends(get_current_user)):
    """
    Retorna os dados do usuário atualmente autenticado.
    """
    return current_user


@router.put("/users/me", response_model=UserResponse)
def update(user_update: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return update_user(db, current_user, user_update.dict(exclude_unset=True))



@router.delete("/users/me", status_code=status.HTTP_204_NO_CONTENT)
def delete(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    delete_user(db, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/users/change-password", status_code=status.HTTP_200_OK)
def change_user_password(
    data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    change_password(db, current_user, data.new_password)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Senha alterada com sucesso."}
    )



@router.get("/motorista/stats/viagens-mes")
def viagens_realizadas_mes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna a quantidade de viagens realizadas pelo motorista no mês atual.
    """
    primeiro_dia_mes = datetime.today().replace(day=1)

    total = (
        db.query(func.count(Checklist.id))
        .filter(
            Checklist.user_id == current_user.id,
            Checklist.data_entrega >= primeiro_dia_mes
        )
        .scalar()
    )

    return {"motorista_id": current_user.id, "viagens_mes_atual": total}