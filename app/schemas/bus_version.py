from pydantic import BaseModel


class BusVersionCreate(BaseModel):
    nome: str

class BusVersionResponse(BaseModel):
    id: int
    nome: str

    model_config = {
        "from_attributes": True
    }
