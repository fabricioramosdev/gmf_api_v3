from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    nome: Optional[str] = None
    cpf: Optional[str] = None
    cnh: Optional[str] = None
    celular: Optional[str] = None
    email: Optional[EmailStr] = None

class UserCreate(UserBase):
    email: str
    password: str

class UserUpdate(UserBase):
    pass

class PasswordChange(BaseModel):
    new_password: str

class UserResponse(UserBase):
    id: int
    email: str
    nome: str

    model_config = {
            "from_attributes": True
        }