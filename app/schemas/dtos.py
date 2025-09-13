from __future__ import annotations
from datetime import datetime

from enum import Enum

from typing import (List, Optional, Annotated)
from pydantic import (BaseModel, Field, field_validator, 
                      ConfigDict, EmailStr, AliasChoices,
                      StringConstraints)

# =============================================================
# Enums
# =============================================================

class ChecklistStatus(str, Enum):
    INICIADO = "INICIADO"
    EM_TRANSPORTE = "EM_TRANSPORTE"
    ENTREGUE = "ENTREGUE"
    CONCLUIDO = "CONCLUIDO"


class InspectionStatus(str, Enum):
    """Status do item inspecionado.

    Use valores curtos e consistentes. Mapeamos entradas comuns para estes três valores.
    """
    OK = "OK"
    REJEITADO = "REJEITADO"
    NA = "NA"


# Mapas de normalização para entradas humanas/despadronizadas
_STATUS_CHECKLIST_NORMALIZE = {
    "iniciado": ChecklistStatus.INICIADO,
    "em transporte": ChecklistStatus.EM_TRANSPORTE,
    "entregue": ChecklistStatus.ENTREGUE,
    "concluído": ChecklistStatus.CONCLUIDO,
}

_STATUS_ITEM_TRUTHY = {"1", "true", "t", "yes", "y", "ok", "sim"}
_STATUS_ITEM_FALSY = {"0", "false", "f", "no", "n", "nok", "nao", "não"}
_STATUS_ITEM_NA = {"na", "n/a", "null", "none", ""}


class DTO(BaseModel):
    # Lê objetos ORM direto e rejeita campos desconhecidos
    model_config = ConfigDict(from_attributes=True, extra="forbid")



# OK
# =============================================================
# Schemas – Login
# =============================================================


class LoginRequest(BaseModel):
    mail: str  #="fabricio.ramos.dev@gmail.com"
    password: str #="admin123"


class Token(BaseModel):
    access_token: str
    token_type: str = "Bearer"


# OK
# =============================================================
# Schemas – Inspection Items 
# =============================================================


class InspectionItemCreate(DTO):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
    mandatory: Optional[bool]  = False            # default igual ao model
    need_for_photo: Optional[bool]  = False       # default igual ao model
    status: Optional[bool]  = True               # default igual ao model (inativo por padrão)

    @field_validator("name", mode="before")
    @classmethod
    def _normalize_name(cls, v):
        return str(v).strip() if v is not None else v

class InspectionItemUpdate(DTO):
    name: Optional[Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]] = None
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



# OK
# =============================================================
# Schemas – User 
# =============================================================


class UserCreate(DTO):
    name: str
    num_cnh:str
    mail: str
    password: str
    phone: Optional[str] = None 
    status: Optional[bool] = True


class UserUpdate(DTO):
    name: Optional[str] = None
    num_cnh: Optional[str] = None
    mail: Optional[str] = None
    phone: Optional[str] =  None
    status: Optional[bool]


class UserOut(DTO):
    id: int
    num_cnh:str
    name: str
    mail: str
    
    class Config:
        from_attributes = True


class PasswordChange(DTO):
    new_password: str


# OK
# =============================================================
# Schemas – Emergency 
# =============================================================

class EmergencyCreate(DTO):
    lat: Optional[float] = None
    long: Optional[float] = None


class EmergencyUpdate(DTO):
    checked: Optional[float] = True


class EmergencyOut(DTO):
    id: int
    fk_user: int
    date_requested: datetime
    lat: Optional[float] = None
    long: Optional[float] = None
    checked: bool
    created_in: datetime

    class Config:
        from_attributes = True


# =============================================================
# Schemas – Checklist Inspected (itens)
# =============================================================

class ChecklistInspectedCreate(DTO):
    fk_item: int = Field(..., description="ID do item de inspeção")
    fk_checklist: int = Field(..., description="ID do Checklist")
    status: InspectionStatus | str = Field(..., description="OK/REJEITADO/NA (aceita variações)")
    fk_photo: Optional[int] = Field(None, description="ID do arquivo de foto (opcional)")

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, v):
        # Aceita Enum direto
        if isinstance(v, InspectionStatus):
            return v
        # Bool → OK/REJEITADO
        if isinstance(v, bool):
            return InspectionStatus.OK if v else InspectionStatus.REJEITADO
        # Numérico → 1=OK, 0=REJEITADO
        try:
            if v is not None and str(v).isdigit():
                return InspectionStatus.OK if int(v) == 1 else InspectionStatus.REJEITADO
        except Exception:
            pass
        s = str(v or "").strip().lower()
        if s in _STATUS_ITEM_TRUTHY:
            return InspectionStatus.OK
        if s in _STATUS_ITEM_FALSY:
            return InspectionStatus.REJEITADO
        if s in _STATUS_ITEM_NA:
            return InspectionStatus.NA
        # Último recurso: tenta casar direto
        s_up = s.upper().replace(" ", "_")
        if s_up in {e.value for e in InspectionStatus}:
            return InspectionStatus(s_up)
        return InspectionStatus.NA  # fallback seguro

    @field_validator("fk_photo", mode="before")
    @classmethod
    def normalize_photo_id(cls, v):
        if v in (None, "", "null", "None", 0, "0", False):
            return None
        try:
            iv = int(v)
            return iv if iv > 0 else None
        except Exception:
            return None


class ChecklistInspectedOut(DTO):
    id: int
    fk_checklist: int
    fk_item: int
    status: InspectionStatus
    fk_photo: Optional[int] = None

    class Config:
        from_attributes = True

# OK
# =============================================================
# Schemas – Checklist 
# =============================================================

class ChecklistCreate(DTO):
    fk_cliente: int
    version_bus: Optional[str] = None
    km_start: Optional[int] = None
    fuel_start: Optional[str] = None
    
    obs: Optional[str] = None
    status: ChecklistStatus = Field(default=ChecklistStatus.INICIADO)

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, v):
        if v is None or isinstance(v, ChecklistStatus):
            return v or ChecklistStatus.INICIADO
        s = str(v).strip().lower()
        if s in _STATUS_CHECKLIST_NORMALIZE:
            return _STATUS_CHECKLIST_NORMALIZE[s]
        return ChecklistStatus(s.upper().replace(" ", "_"))


class ChecklistUpdate(DTO):
    fk_cliente: Optional[int] = None
    version_bus: Optional[str] = None
    km_start: Optional[int] = None
    fuel_start: Optional[str] = None
    km_end: Optional[int] = None
    fuel_end: Optional[str] = None
    obs: Optional[str] = None
    status: Optional[ChecklistStatus] = None

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, v):
        if v is None or isinstance(v, ChecklistStatus):
            return v
        s = str(v).strip().lower()
        if s in _STATUS_CHECKLIST_NORMALIZE:
            return _STATUS_CHECKLIST_NORMALIZE[s]
        return ChecklistStatus(s.upper().replace(" ", "_"))


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
    status: ChecklistStatus
    obs: Optional[str] = None

    class Config:
        from_attributes = True


class ChecklistDetailOut(ChecklistOut):
    itens: List[ChecklistInspectedOut] = Field(default_factory=list)



# =============================================================
# Schemas - Client 
# =============================================================

# --- CLIENT SCHEMAS ---
class ClientCreate(DTO):
    name: str 
    phone: Optional[str] = None
    mail: Optional[EmailStr] = None
    status: Optional[bool] = True


class ClientOut(DTO):
    id: int
    name: str
    mail: Optional[EmailStr] = None

    class Config:
        from_attributes = True



# =============================================================
# Schemas – UploadFolder 
# =============================================================

class UploadFolderCreate(DTO):
    folder_hash: str
    # aceita fk_user OU user_id
    fk_user: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices("fk_user", "user_id"),
    )
    # aceita fk_checklist OU checklist_id
    fk_checklist: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices("fk_checklist", "checklist_id"),
    )

    


class UploadFolderUpdate(DTO):
    folder_hash: Optional[str] = None
    fk_user: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices("fk_user", "user_id"),
    )
    fk_checklist: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices("fk_checklist", "checklist_id"),
    )

class UploadFolderOut(DTO):
    id: int
    folder_hash: str
    fk_user: Optional[int] = Field(default=None, serialization_alias="user_id")
    fk_checklist: Optional[int] = Field(default=None, serialization_alias="checklist_id")
    created_in: datetime

    class Config:
        from_attributes = True


# =============================================================
# Schemas – UploadFile
# =============================================================

class UploadFileCreate(DTO):
    file_name: str
    file_url: str  # se quiser validar URL, troque para AnyUrl
    # aceita fk_folder OU folder_id no payload
    fk_folder: int = Field(validation_alias=AliasChoices("fk_folder", "folder_id"))

    @field_validator("file_name", mode="before")
    @classmethod
    def _strip_filename(cls, v):
        return str(v).strip() if v is not None else v

class UploadFileUpdate(DTO):
    file_name: Optional[str] = None
    file_url: Optional[str] = None
    fk_folder: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices("fk_folder", "folder_id"),
    )

class UploadFileOut(DTO):
    id: int
    file_name: str
    file_url: str
    # devolve como folder_id para ficar mais “restful”
    fk_folder: int = Field(serialization_alias="folder_id")
    created_in: datetime

    class Config:
        from_attributes = True
