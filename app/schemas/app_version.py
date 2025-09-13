from pydantic import BaseModel
from datetime import datetime

class AppVersionCreate(BaseModel):
    version: str
    platform: str

class AppVersionResponse(BaseModel):
    id: int
    version: str
    platform: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }