#schemas\checklist.py

from pydantic import BaseModel, field_validator, field_serializer
from typing import Optional, List
from datetime import datetime


class ChecklistInspectedCreate(BaseModel):
    inspection_item_id: int
    status: str
    foto_id: Optional[int] = None

    @field_validator("foto_id", mode="before")
    @classmethod
    def normalize_foto_id(cls, v):
        if v in (None, "", "null", "None", 0, "0", False):
            return None
        try:
            iv = int(v)
            return iv if iv > 0 else None
        except Exception:
            return None


class ChecklistInspectedResponse(BaseModel):
    inspection_item_id: int
    status: str
    foto_id: Optional[int] = None

    model_config = {
        "from_attributes": True
    }


class ChecklistCreate(BaseModel):

    cliente_id: int
    versao_onibus: Optional[str]= None
    km_saida: Optional[str]= None
    km_chegada: Optional[str]= None
    foto_painel_saida: Optional[str]= None
    foto_painel_chegada: Optional[str]= None
    combustivel_chegada: Optional[str]= None
    combustivel_saida: Optional[str]= None
    observacoes: Optional[str]= None



class ChecklistResponse(BaseModel):
    id:int
    cliente_id: int
    versao_onibus: Optional[str]= None
    km_saida: Optional[str]= None
    km_chegada: Optional[str]= None
    foto_painel_saida: Optional[str]= None
    foto_painel_chegada: Optional[str]= None
    combustivel_chegada: Optional[str]= None
    combustivel_saida: Optional[str]= None
    observacoes: Optional[str]= None
    iniciado_em: datetime  

    @field_serializer('iniciado_em')
    def serialize_iniciado(self, v: datetime) -> str:
        return v.strftime('%Y-%m-%d %H:%M:%S')



class ItemFotoAssociation(BaseModel):
    item_inspected_id: int
    foto_id: int

class ItemFotoAssociationRequest(BaseModel):
    associations: list[ItemFotoAssociation]