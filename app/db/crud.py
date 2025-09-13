from sqlalchemy import desc
from sqlalchemy.orm import Session


from typing import List, Optional

from app.db.models import (User, Client, InspectionItem,
                             UploadFolder, UploadFile, 
                             EmergencyRequests, Checklist, ChecklistItemsInspected, 
                             Checklist, InspectionItem
                             )

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


def user_is_admin(user: User) -> bool:
    return getattr(user, "is_admin", False) or str(getattr(user, "role", "")).lower() == "admin"

#===================================================================================================================================
# --- CRUD para Dropbox ---
#===================================================================================================================================
def save_upload(db: Session, folder_hash: str, files: dict, user_id:  Optional[int] = None,  checklist_id: Optional[int] = None):
    folder = UploadFolder(folder_hash=folder_hash, fk_user=user_id, checklist_id=checklist_id)
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
#--- CRUD para InspectionItem  ---
#================================================================================================

def create_inspection_item(
    db: Session,
    name: str,
    status: Optional[bool] = True,
    mandatory: Optional[bool] = False,
    need_for_photo: Optional[bool] = False
) -> InspectionItem:
    item = InspectionItem(
        name=name,
        status=status,
        mandatory=mandatory,
        need_for_photo=need_for_photo
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_all_inspection_items(db: Session) -> List[InspectionItem]:
    return (
        db.query(InspectionItem)
          .order_by(
               InspectionItem.need_for_photo.desc(),  # True primeiro
              InspectionItem.name.asc(),              # A→Z
              InspectionItem.id.asc(),                # tie-break estável
          )
          .all()
    )


def get_inspection_item_by_id(db: Session, item_id: int) -> Optional[InspectionItem]:
    return db.query(InspectionItem).filter(InspectionItem.id == item_id).first()


def update_inspection_item(db: Session, item: InspectionItem, updates: dict) -> InspectionItem:
    for key, value in updates.items():
        if hasattr(item, key):
            setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


def delete_inspection_item(db: Session, item: InspectionItem):
    db.delete(item)
    db.commit()


# =====================================================================================
# --- CRUD para S.O.S ---
#======================================================================================
def create_emergency_request(db: Session, user_id: int, lat: Optional[float], long: Optional[float]) -> EmergencyRequests:

    request = EmergencyRequests(
        fk_user=user_id,
        lat=lat,
        long=long
    )
    
    db.add(request)
    db.commit()
    db.refresh(request)

    return request


def get_emergency_requests(db: Session) -> List[EmergencyRequests]:
    return db.query(EmergencyRequests).all()


def get_emergency_request_by_id(db: Session, request_id: int) -> Optional[EmergencyRequests]:
    return db.query(EmergencyRequests).filter(EmergencyRequests.id == request_id).first()


def verify_emergency_request(db: Session, request: EmergencyRequests) -> EmergencyRequests:
    request.checked = True
    db.commit()
    db.refresh(request)
    return request

#=====================================================================================
#---- CRUD para Checklist ---
#=====================================================================================

def get_checklist_by_id_for_user(db: Session, checklist_id: int, user: User) -> Optional[Checklist]:
    q = db.query(Checklist).filter(Checklist.id == checklist_id)
    if not user_is_admin(user):
        q = q.filter(Checklist.fk_user == user.id)
    return q.first()


def get_all_checklists(db: Session) -> List[Checklist]:
    return db.query(Checklist).all()


def get_checklist_by_id(db: Session, checklist_id: int) -> Checklist:
    return db.query(Checklist).filter(Checklist.id == checklist_id).first()


def list_all_checklists(db: Session, user_id: int) -> List[Checklist]:
    return db.query(Checklist).filter(Checklist.fk_user == user_id).all()



#=====================================================================================
#---- CRUD para ChecklistItemsInspected ---         
#=====================================================================================

def get_checklist_item(db: Session, checklist_id: int, item_id: int) -> Optional[ChecklistItemsInspected]:
    return (
        db.query(ChecklistItemsInspected)
          .filter(
              ChecklistItemsInspected.fk_checklist == checklist_id,
              ChecklistItemsInspected.fk_item == item_id,
          )
          .first()
    )

def add_item_to_checklist(
    db: Session,
    *,
    checklist_id: int,
    item_id: int,
    status: str,
    photo_id: Optional[int],
) -> ChecklistItemsInspected:
    # sanity checks opcionais
    if not db.get(Checklist, checklist_id):
        raise ValueError("Checklist inexistente.")
    if not db.get(InspectionItem, item_id):
        raise ValueError("InspectionItem inexistente.")

    exists = get_checklist_item(db, checklist_id, item_id)
    if exists:
        # se preferir 409 na rota, apenas retorne exists e trate lá
        return exists

    obj = ChecklistItemsInspected(
        fk_checklist=checklist_id,
        fk_item=item_id,
        status=status,
        fk_foto=photo_id,   # nome do model
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def update_checklist_item(
    db: Session,
    *,
    checklist_id: int,
    item_id: int,
    data: dict,
) -> Optional[ChecklistItemsInspected]:
    obj = get_checklist_item(db, checklist_id, item_id)
    if not obj:
        return None
    if "status" in data and data["status"] is not None:
        obj.status = data["status"]
    if "photo_id" in data:
        obj.fk_foto = data["photo_id"]
    db.commit()
    db.refresh(obj)
    return obj

def delete_checklist_item(db: Session, *, checklist_id: int, item_id: int) -> bool:
    obj = get_checklist_item(db, checklist_id, item_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True

def bulk_add_items(
    db: Session,
    *,
    checklist_id: int,
    items: List[dict],
    upsert: bool = True,
) -> List[ChecklistItemsInspected]:
    """Cria vários itens; se upsert=True, atualiza status/foto se já existir."""
    out = []
    for it in items:
        existing = get_checklist_item(db, checklist_id, it["item_id"])
        if existing:
            if upsert:
                if "status" in it:   existing.status = it["status"]
                if "photo_id" in it: existing.fk_foto = it["photo_id"]
                out.append(existing)
            # se não for upsert, apenas ignora
        else:
            obj = ChecklistItemsInspected(
                fk_checklist=checklist_id,
                fk_item=it["item_id"],
                status=it.get("status", "NA"),
                fk_foto=it.get("photo_id"),
            )
            db.add(obj)
            out.append(obj)
    db.commit()
    # refresh opcional (se precisa de ids/fks na resposta)
    for obj in out: db.refresh(obj)
    return out