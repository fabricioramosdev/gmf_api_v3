from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EmergencyRequestCreate(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class EmergencyRequestResponse(BaseModel):
    id: int
    user_id: int
    timestamp: datetime
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    verificado: bool

    model_config = {
        "from_attributes": True
    }