from fastapi import APIRouter

from .auth import router as router_auth
from .user import router as router_user
from .client import router as router_client
from .items import router as router_items
from .sos import router as router_sos
from .dropbox import router as router_dropbox
from .checklist import router as router_checklist

from .items_has_checklist import router as router_items_has_checklist


api_v3 = APIRouter(prefix="/v3")

api_v3.include_router(router_auth)
api_v3.include_router(router_items_has_checklist)
api_v3.include_router(router_checklist) 
api_v3.include_router(router_dropbox)
api_v3.include_router(router_sos)
api_v3.include_router(router_items)
api_v3.include_router(router_client)
api_v3.include_router(router_user)

