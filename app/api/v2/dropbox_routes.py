from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional
from sqlalchemy.orm import Session

# Serviços de integração com Dropbox
from app.services.dropbox_service import (
    upload_files_to_dropbox,
    create_new_folder,
    list_files_in_folder,
    get_dropbox_access_token
)

# Dependências e utilitários
from app.core.dependencies import get_current_user
from app.services.audit_service import log_action
from app.db.session import get_db
from app.db.crud import save_upload

# Esquema OAuth2 de autenticação por token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v2/login")

# Instância do roteador FastAPI
router = APIRouter()

# 📤 Rota para upload de múltiplos arquivos para o Dropbox
@router.post("/upload/")
async def upload_multiple_files(
    files: List[UploadFile] = File(...),                   # Lista de arquivos recebidos
    folder_name: Optional[str] = Form(None),               # Nome da pasta opcional
    checklist_id: Optional[int] = Form(None),              # ID do checklist (opcional)
    current_user: str = Depends(get_current_user),         # Usuário autenticado
    db: Session = Depends(get_db)                          # Sessão do banco
):
    
    
    """
    Faz upload de múltiplos arquivos para o Dropbox e salva os metadados no banco.
    Opcionalmente vincula os arquivos a um checklist específico.
    """
    
    
    try:
        # Lê o conteúdo dos arquivos
        file_dict = {file.filename: await file.read() for file in files}

        # Envia para o Dropbox
        folder, uploaded_files = upload_files_to_dropbox(file_dict, folder_name)

        # Salva metadados no banco vinculando ao usuário e (opcionalmente) ao checklist
        saved = save_upload(
            db=db,
            folder_hash=folder,
            files=uploaded_files,
            user_id=current_user.id,
            checklist_id=checklist_id
        )

        return {
            "message": "Upload concluído!",
            "checklist": checklist_id,
            "folder": folder,           
            "files": saved
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# 📁 Cria uma nova pasta no Dropbox
@router.post("/create-folder/")
def create_folder(
    folder_name: Optional[str] = Form(None),
    current_user: str = Depends(get_current_user)
):
    """
    Cria uma nova pasta no Dropbox para armazenar arquivos.
    """
    try:
        folder_info = create_new_folder(folder_name)
        return {
            "message": "Pasta criada com sucesso!",
            "folder": folder_info["folder"],
            "path": folder_info["path"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 📂 Lista os arquivos de uma pasta no Dropbox
@router.get("/list-files/")
def list_files(folder_hash: str, current_user: str = Depends(get_current_user)):
    """
    Lista os arquivos de uma pasta específica no Dropbox.
    """
    try:
        files = list_files_in_folder(folder_hash)
        return {"folder": folder_hash, "files": files}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# 🔐 Recupera o token de acesso atual do Dropbox
@router.get("/get-dropbox-token/")
def get_token(current_user: str = Depends(get_current_user)):
    """
    Retorna o token de acesso do Dropbox (útil para debug ou testes).
    """
    try:
        access_token = get_dropbox_access_token()
        return {"access_token": access_token}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
