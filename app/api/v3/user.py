
from fastapi import APIRouter, Response, Depends, HTTPException, Path, status
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session




from app.db.session import get_db
from app.db.models import User
from app.db.crud import (create_user, get_user, update_user, 
                         delete_user, change_password,get_user_by_id
)
from app.schemas.dtos import (UserCreate, UserUpdate, PasswordChange, 
                              UserOut)


from app.services.audit_service import log_action
from app.core.dependencies import get_current_user
from app.core.security import get_password_hash



router = APIRouter(prefix="/users", tags=["User"])

@router.post("/", response_model=UserOut)
def create(user_data: UserCreate, db: Session = Depends(get_db)):
    if get_user(db, user_data.mail):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Usuário já existe")
    
    log_action(
        action="create clients",
        previous_data={},
        current_data=user_data.model_dump(),
        db=db,
        current_user=get_current_user
    )

  
    return create_user(
                        db,
                        name=user_data.name,
                        mail=user_data.mail,                
                        password=user_data.password,
                        **user_data.dict(exclude={"password", "mail", "name"})
                    )


@router.get("/", response_model=UserOut)
def get_logged_in_user(current_user: User = Depends(get_current_user)):
    """
    Retorna os dados do usuário atualmente autenticado.
    """
    return current_user



# --- 1) Trocar senha do PRÓPRIO usuário (/users/change-password) ---
@router.put("/change-password", status_code=204)
def change_my_password(
    payload: PasswordChange,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    hpw = get_password_hash(payload.new_password)

    log_action(
        action="change password",
        previous_data={},
        current_data={},
        db=db,
        current_user=get_current_user
    )

    update_user(db, current_user, {"hashed_password": hpw})
    return  # 204 No Content


# --- 2) Trocar senha por ID (admin) (/users/{user_id}/change-password) ---
@router.put("/{user_id}/change-password", status_code=204)
def change_password_by_id(
    user_id: int = Path(..., ge=1),
    payload: PasswordChange = ...,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    is_admin = getattr(current_user, "is_admin", False)
    if not is_admin and user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sem permissão.")
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    hpw = get_password_hash(payload.new_password)
    update_user(db, user, {"hashed_password": hpw})
    return  # 204 No Content



@router.put("/{user_id}", response_model=UserOut)
def update_user_route(
    user_id: int = Path(..., ge=1),
    payload: UserUpdate = ...,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    # Autorização: o próprio usuário OU admin (ajuste a flag conforme seu modelo)
    is_admin = getattr(current_user, "is_admin", False)
    if user_id != current_user.id and not is_admin:
        raise HTTPException(status_code=403, detail="Sem permissão para editar este usuário.")

    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    data = payload.model_dump(exclude_unset=True)  # Pydantic v2
    # se vier 'password', converta para hashed_password e remova do payload
    if "password" in data:
        data["hashed_password"] = get_password_hash(data.pop("password"))
    # normalização de email (se aplicável)
    if "mail" in data and data["mail"]:
        data["mail"] = data["mail"].strip().lower()

    updated = update_user(db, user, data)  # ou update_user_by_id(db, user_id, data)
    return updated


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_by_id(
    user_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    # regra: pode apagar a si mesmo; para apagar outro, precisa ser admin
    is_admin = getattr(current_user, "is_admin", False)
    if user_id != current_user.id and not is_admin:
        raise HTTPException(status_code=403, detail="Sem permissão para excluir este usuário.")

    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    delete_user(db, user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
