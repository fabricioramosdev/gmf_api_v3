from pydantic import BaseModel
from typing import Optional

class InspectionItemCreate(BaseModel):
    nome: str
    status: Optional[bool] = True
    obrigatorio: Optional[bool] = False
    foto: Optional[bool] = False  # Novo campo

class InspectionItemResponse(BaseModel):
    id: int
    nome: str
    status: bool
    obrigatorio: bool
    foto: bool  # Novo campo

    model_config = {
        "from_attributes": True
    }
