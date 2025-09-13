
from datetime import datetime
from typing import (Optional, List)
from pydantic import Field, AliasChoices, field_validator, computed_field

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    ConfigDict,
    EmailStr,
    AliasChoices
)

# =============================================================
# Status de Checklist: códigos, rótulos e mapeamentos
# =============================================================
CHECKLIST_STATUS_CODE_TO_LABEL = {
    1: "Iniciado",
    2: "Transporte",
    3: "Entrega",
    4: "Concluido",
}
CHECKLIST_STATUS_CODE_TO_DB = {
    1: "INICIADO",
    2: "EM_TRANSPORTE",
    3: "ENTREGUE",
    4: "CONCLUIDO",
}
CHECKLIST_STATUS_DB_TO_CODE = {v: k for k, v in CHECKLIST_STATUS_CODE_TO_DB.items()}

CHECKLIST_STATUS_LABEL_TO_CODE = {
    "iniciado": 1, "1": 1,
    "transporte": 2, "em_transporte": 2, "em transporte": 2, "2": 2,
    "entrega": 3, "entregue": 3, "3": 3,
    "concluido": 4, "concluído": 4, "4": 4,
}

# normalização simples
_TRUTHY = {"1","true","t","yes","y","ok","sim"}
_FALSY  = {"0","false","f","no","n","nok","nao","não"}
_NA     = {"na","n/a","null","none",""}


# normalização simples
_TRUTHY = {"1","true","t","yes","y","ok","sim"}
_FALSY  = {"0","false","f","no","n","nok","nao","não"}
_NA     = {"na","n/a","null","none",""}


class DTO(BaseModel):
    """Base de todos os DTOs."""
    model_config = ConfigDict(from_attributes=True, extra="forbid")



# =============================================================
# Schemas – Items no Checklist
# =============================================================

class ChecklistItemCreate(DTO):
    item_id: int = Field(validation_alias=AliasChoices("item_id", "fk_item"))
    status: str = Field(default="NA", description="OK | REJEITADO | NA")
    photo_id: Optional[int] = Field(default=None, validation_alias=AliasChoices("photo_id","fk_photo","foto_id"))

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, v):
        if isinstance(v, bool): return "OK" if v else "REJEITADO"
        s = str(v or "").strip().lower()
        if s in _TRUTHY: return "OK"
        if s in _FALSY:  return "REJEITADO"
        if s in _NA:     return "NA"
        su = s.upper().replace(" ", "_")
        return su if su in {"OK","REJEITADO","NA"} else "NA"

    @field_validator("photo_id", mode="before")
    @classmethod
    def normalize_photo(cls, v):
        if v in (None, "", "null", "None", 0, "0", False): return None
        try:
            iv = int(v);  return iv if iv > 0 else None
        except: return None

class ChecklistItemUpdate(DTO):
    status: Optional[str] = None
    photo_id: Optional[int] = Field(default=None, validation_alias=AliasChoices("photo_id","fk_photo","foto_id"))

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, v):
        if v is None: return None
        if isinstance(v, bool): return "OK" if v else "REJEITADO"
        s = str(v or "").strip().lower()
        if s in _TRUTHY: return "OK"
        if s in _FALSY:  return "REJEITADO"
        if s in _NA:     return "NA"
        su = s.upper().replace(" ", "_")
        return su if su in {"OK","REJEITADO","NA"} else None

class ChecklistItemOut(DTO):
    id: int
    # lê do atributo ORM fk_checklist / fk_item, MAS responde como checklist_id / item_id
    checklist_id: int = Field(validation_alias=AliasChoices("checklist_id", "fk_checklist"))
    item_id: int = Field(validation_alias=AliasChoices("item_id", "fk_item"))

    status: str

    # foto pode estar como fk_foto / fk_photo / foto_id no ORM/banco
    photo_id: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices("photo_id", "fk_foto", "fk_photo", "foto_id"),
    )

    # inclua se existir no model
    # created_in: datetime

class ChecklistItemsBulkCreate(DTO):
    items: List[ChecklistItemCreate]


# =============================================================
# Schemas – Login
# =============================================================

class LoginRequest(BaseModel):
    mail: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "Bearer"



# ===============================================================
# Schemas – 
#============================================================

# =============================================================
# Schemas – Inspection Items
# =============================================================

class InspectionItemCreate(DTO):
    name: Optional[str] = None
    mandatory: Optional[bool] = False
    need_for_photo: Optional[bool] = False
    status: Optional[bool] = True

    @field_validator("name", mode="before")
    @classmethod
    def _normalize_name(cls, v):
        return str(v).strip() if v is not None else v

class InspectionItemUpdate(DTO):
    name: Optional[str] = None
    mandatory: Optional[bool] = None
    need_for_photo: Optional[bool] = None
    status: Optional[bool] = None

    @field_validator("name", mode="before")
    @classmethod
    def _normalize_name(cls, v):
        return str(v).strip() if v is not None else v

class InspectionItemOut(DTO):
    id: int
    name: str
    mandatory: bool
    need_for_photo: bool
    status: bool
    created_in: datetime


# =============================================================
# Schemas – User
# =============================================================

class UserCreate(DTO):
    name: str
    num_cnh: str
    mail: str
    password: str
    phone: Optional[str] = None
    status: Optional[bool] = True

class UserUpdate(DTO):
    name: Optional[str] = None
    num_cnh: Optional[str] = None
    mail: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[bool] = None

class UserOut(DTO):
    id: int
    num_cnh: str
    name: str
    mail: str

class PasswordChange(DTO):
    new_password: str


# =============================================================
# Schemas – Emergency
# =============================================================

class EmergencyCreate(DTO):
    lat: Optional[float] = None
    long: Optional[float] = None

class EmergencyUpdate(DTO):
    checked: Optional[bool] = True

class EmergencyOut(DTO):
    id: int
    fk_user: int
    date_requested: datetime
    lat: Optional[float] = None
    long: Optional[float] = None
    checked: bool
    created_in: datetime


# =============================================================
# Schemas – Checklist
# =============================================================
class ChecklistCreate(DTO):
    fk_cliente: int
    version_bus: Optional[str] = None
    km_start: Optional[int] = None
    fuel_start: Optional[str] = None
    obs: Optional[str] = None
    # aceita 'status_code' (novo) ou legado 'status'
    status_code: int = Field(default=1, ge=1, le=4,
                             validation_alias=AliasChoices("status_code", "status"))

    @field_validator("status_code", mode="before")
    @classmethod
    def _norm_code(cls, v):
        if v is None: return 1
        try:
            iv = int(v);  return iv if 1 <= iv <= 4 else 1
        except: pass
        return CHECKLIST_STATUS_LABEL_TO_CODE.get(str(v).strip().lower(), 1)

    # opcional: manter compat de quem ainda lê 'status' string do request DTO
    @computed_field
    @property
    def status(self) -> str:
        return CHECKLIST_STATUS_CODE_TO_DB.get(self.status_code, "INICIADO")


class ChecklistUpdate(DTO):
    fk_cliente: Optional[int] = None
    version_bus: Optional[str] = None
    km_start: Optional[int] = None
    fuel_start: Optional[str] = None
    km_end: Optional[int] = None
    fuel_end: Optional[str] = None
    obs: Optional[str] = None
    status_code: Optional[int] = Field(default=None,
                                       validation_alias=AliasChoices("status_code", "status"))

    @field_validator("status_code", mode="before")
    @classmethod
    def _norm_code(cls, v):
        if v is None: return None
        try:
            iv = int(v);  return iv if 1 <= iv <= 4 else None
        except: pass
        return CHECKLIST_STATUS_LABEL_TO_CODE.get(str(v).strip().lower(), None)


class ChecklistOut(DTO):
    id: int
    fk_user: int
    fk_cliente: int
    version_bus: Optional[str] = None
    km_start: Optional[int] = None
    fuel_start: Optional[str] = None
    date_start: datetime
    km_end: Optional[int] = None
    fuel_end: Optional[str] = None
    date_end: Optional[datetime] = None
    status: str           # ← vem do model (sem alterar o model)
    obs: Optional[str] = None

    @computed_field
    @property
    def status_code(self) -> int:
        return CHECKLIST_STATUS_DB_TO_CODE.get(self.status, 1)

    @computed_field
    @property
    def status_label(self) -> str:
        return CHECKLIST_STATUS_CODE_TO_LABEL.get(self.status_code, "Iniciado")
# =============================================================
# Schemas – Client
# =============================================================

class ClientCreate(DTO):
    name: str
    phone: Optional[str] = None
    mail: Optional[EmailStr] = None
    status: Optional[bool] = True

class ClientUpdate(DTO):
    name: Optional[str] = None
    phone: Optional[str] = None
    mail: Optional[EmailStr] = None
    status: Optional[bool] = None

class ClientOut(DTO):
    id: int
    name: str
    mail: Optional[EmailStr] = None


# =============================================================
# Schemas – UploadFolder
# =============================================================

class UploadFolderCreate(DTO):
    folder_hash: str
    fk_user: Optional[int] = Field(default=None, validation_alias=AliasChoices("fk_user", "user_id"))
    fk_checklist: Optional[int] = Field(default=None, validation_alias=AliasChoices("fk_checklist", "checklist_id"))

class UploadFolderUpdate(DTO):
    folder_hash: Optional[str] = None
    fk_user: Optional[int] = Field(default=None, validation_alias=AliasChoices("fk_user", "user_id"))
    fk_checklist: Optional[int] = Field(default=None, validation_alias=AliasChoices("fk_checklist", "checklist_id"))

class UploadFolderOut(DTO):
    id: int
    folder_hash: str
    fk_user: Optional[int] = Field(default=None, serialization_alias="user_id")
    fk_checklist: Optional[int] = Field(default=None, serialization_alias="checklist_id")
    created_in: datetime


# =============================================================
# Schemas – UploadFile
# =============================================================

class UploadFileCreate(DTO):
    file_name: str
    file_url: str
    fk_folder: int = Field(validation_alias=AliasChoices("fk_folder", "folder_id"))

    @field_validator("file_name", mode="before")
    @classmethod
    def _strip_filename(cls, v):
        return str(v).strip() if v is not None else v

class UploadFileUpdate(DTO):
    file_name: Optional[str] = None
    file_url: Optional[str] = None
    fk_folder: Optional[int] = Field(default=None, validation_alias=AliasChoices("fk_folder", "folder_id"))

class UploadFileOut(DTO):
    id: int
    file_name: str
    file_url: str
    fk_folder: int = Field(serialization_alias="folder_id")
    created_in: datetime

