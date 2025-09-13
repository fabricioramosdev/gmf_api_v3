from pydantic import BaseModel, EmailStr
from typing import Optional

# --- CLIENT SCHEMAS ---
class ClientCreate(BaseModel):
    nome: str
    email: Optional[EmailStr] = None

class ClientResponse(BaseModel):
    id: int
    nome: str
    email: Optional[EmailStr] = None

    model_config = {
        "from_attributes": True
    }