#db\crud.py

from sqlalchemy import desc
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from typing import List, Optional

from fastapi import Depends, HTTPException, status

from app.db.models import (User, Client,  UploadFolder, UploadFile)
from app.core.security import get_password_hash

#====================================================================================
# --- CRUD para User ---
#====================================================================================

def create_user(db: Session, mail: str, password: str, **kwargs) -> User:
    hashed_pw = get_password_hash(password)
    user = User(mail=mail, hashed_password=hashed_pw, **kwargs)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user: User, data: dict):
    for k, v in data.items():
        setattr(user, k, v)
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, mail: str):
    return db.query(User).filter(User.mail == mail).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def delete_user(db: Session, user: User):
    db.delete(user)
    db.commit()


def change_password(db: Session, user: User, new_password: str):
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    db.refresh(user)
    return user

#===================================================================================================================================
# --- CRUD para Dropbox ---
#===================================================================================================================================

def save_upload(db: Session, folder_hash: str, files: dict, user_id:  Optional[int] = None,  checklist_id: Optional[int] = None):
    folder = UploadFolder(folder_hash=folder_hash, user_id=user_id, checklist_id=checklist_id)
    db.add(folder)
    db.flush()  # garante que o folder_id é gerado antes de criar arquivos

    files_saved = []
    for file_name, file_url in files.items():
        upload_file = UploadFile(file_name=file_name, file_url=file_url, folder=folder)
 
        db.add(upload_file)
        db.flush()
        files_saved.append({'upload_file':upload_file.id, 'file_name':upload_file.file_name, 'file_url':upload_file.file_url})
       
    db.commit()
    db.refresh(folder)
    return {'folder':folder, 'files': files_saved}


#====================================================================================================================
# --- CRUD para Client ---
#====================================================================================================================
def create_client(db: Session, name: str, mail: Optional[str] = None,  phone: Optional[str] = None) -> Client:
    client = Client(name=name, mail=mail, phone=phone)
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def get_client_by_id(db: Session, client_id: int) -> Optional[Client]:
    return db.query(Client).filter(Client.id == client_id).first()


def get_all_clients(db: Session) -> List[Client]:
    return (
        db.query(Client)
          .order_by(desc(Client.frequency_order), Client.name.asc())  # tie-break por nome
          .all()
    )


def update_client(db: Session, client: Client, updates: dict) -> Client:
    for key, value in updates.items():
        setattr(client, key, value)
    db.commit()
    db.refresh(client)
    return client


def delete_client(db: Session, client: Client):
    db.delete(client)
    db.commit()


#================================================================================================
#================================================================================================
"""

#---- CRUD para InspectionItem  ---
# --- CREATE ---

def create_inspection_item(
    db: Session,
    nome: str,
    status: Optional[bool] = True,
    obrigatorio: Optional[bool] = False,
    foto: Optional[bool] = False  # Novo campo
) -> InspectionItem:
    item = InspectionItem(
        nome=nome,
        status=status,
        obrigatorio=obrigatorio,
        foto=foto
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

# --- READ ---
def get_all_inspection_items(db: Session) -> List[InspectionItem]:
    return db.query(InspectionItem).all()


def get_inspection_item_by_id(db: Session, item_id: int) -> Optional[InspectionItem]:
    return db.query(InspectionItem).filter(InspectionItem.id == item_id).first()


# --- UPDATE ---
def update_inspection_item(db: Session, item: InspectionItem, updates: dict) -> InspectionItem:
    for key, value in updates.items():
        if hasattr(item, key):
            setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


# --- DELETE ---
def delete_inspection_item(db: Session, item: InspectionItem):
    db.delete(item)
    db.commit()


#---- CRUD para Checklist ---
def create_checklist(db: Session, checklist: 
                     ChecklistCreate, user_id: int) -> Checklist:

    try:
        checklist = Checklist(
         
            cliente_id=checklist.cliente_id,
            versao_onibus=checklist.versao_onibus,
            km_saida=checklist.km_saida,
            km_chegada=checklist.km_chegada,
            foto_painel_saida=checklist.foto_painel_saida,
            foto_painel_chegada=checklist.foto_painel_chegada,
            combustivel_saida=checklist.combustivel_saida,
            combustivel_chegada=checklist.combustivel_chegada,
            observacoes=checklist.observacoes,
            user_id=user_id
        )
        db.add(checklist)
        db.commit()
        db.refresh(checklist)

    except Exception as e:
        db.rollback()
    
    return checklist

def get_all_checklists(db: Session) -> List[Checklist]:
    return db.query(Checklist).all()

def get_checklist_by_id(db: Session, checklist_id: int) -> Checklist:
    return db.query(Checklist).filter(Checklist.id == checklist_id).first()


def list_all_checklists(db: Session, user_id: int) -> List[Checklist]:
    #print(owner_id)
    #import pdb; 
    #pdb.set_trace()
    return db.query(Checklist).filter(Checklist.user_id == user_id).all()


def add_inspected_items(
    db: Session, 
    checklist_id: int, 
    itens: List[ChecklistInspectedCreate]
):
   
    try:
        inspected_items = []
        for item in itens:
            inspected = ChecklistInspected(
                checklist_id=checklist_id,
                inspection_item_id=item.inspection_item_id,
                status=item.status,
                foto_id=item.foto_id
            )
            db.add(inspected)
            inspected_items.append(inspected)

        db.commit()

        ids_criados = [item.id for item in inspected_items]

        return {"message": "Itens adicionados com sucesso.", "ids": ids_criados}
    
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Erro ao adicionar itens inspecionados: {str(e)}")

# --- CRUD para ChecklistInspected ---
def create_checklist_inspected(db: Session, item_data: ChecklistInspectedCreate) -> ChecklistInspected:
    item = ChecklistInspected(
        checklist_id=item_data.checklist_id,
        inspection_item_id=item_data.inspection_item_id,
        status=item_data.status,
        foto_id=item_data.foto_id
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_all_checklist_inspected(db: Session) -> List[ChecklistInspected]:
    return db.query(ChecklistInspected).all()


def get_checklist_inspected_by_checklist(db: Session, checklist_id: int) -> List[ChecklistInspected]:
    return db.query(ChecklistInspected).filter(ChecklistInspected.checklist_id == checklist_id).all()


from sqlalchemy.orm import Session
from app.db.models import ChecklistInspected, UploadFile

def associate_photos_to_inspected_items(
    db: Session,
    associations: list[dict]
):
    for association in associations:
        inspected_item = db.query(ChecklistInspected).filter(
            ChecklistInspected.id == association["item_inspected_id"]
        ).first()

        if inspected_item is None:
            raise ValueError(f"Item inspecionado não encontrado (id={association['item_inspected_id']})")

        foto = db.query(UploadFile).filter(
            UploadFile.id == association["foto_id"]
        ).first()

        if foto is None:
            raise ValueError(f"Arquivo de foto não encontrado (id={association['foto_id']})")

        inspected_item.foto = foto

    db.commit()


def create_emergency_request(db: Session, user_id: int, latitude: Optional[float], longitude: Optional[float]) -> EmergencyRequest:
    request = EmergencyRequest(
        user_id=user_id,
        latitude=latitude,
        longitude=longitude
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request

def get_emergency_requests(db: Session) -> List[EmergencyRequest]:
    return db.query(EmergencyRequest).all()

def get_emergency_request_by_id(db: Session, request_id: int) -> Optional[EmergencyRequest]:
    return db.query(EmergencyRequest).filter(EmergencyRequest.id == request_id).first()

def verify_emergency_request(db: Session, request: EmergencyRequest) -> EmergencyRequest:
    request.verificado = True
    db.commit()
    db.refresh(request)
    return request


def create_app_version(db: Session, version: str, platform: str) -> AppVersion:
    entry = AppVersion(version=version, platform=platform)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

def get_latest_app_version(db: Session, platform: str) -> AppVersion:
    return db.query(AppVersion).filter(AppVersion.platform == platform).order_by(AppVersion.created_at.desc()).first()

def get_all_app_versions(db: Session) -> List[AppVersion]:
    return db.query(AppVersion).order_by(AppVersion.created_at.desc()).all()



def create_bus_version(db: Session, nome: str) -> BusVersion:
    version = BusVersion(nome=nome)
    db.add(version)
    db.commit()
    db.refresh(version)
    return version

def get_all_bus_versions(db: Session) -> List[BusVersion]:
    return db.query(BusVersion).order_by(BusVersion.nome).all()

def get_bus_version_by_id(db: Session, version_id: int) -> Optional[BusVersion]:
    return db.query(BusVersion).filter(BusVersion.id == version_id).first()


def delete_bus_version(db: Session, version: BusVersion):
    db.delete(version)
    db.commit()
"""