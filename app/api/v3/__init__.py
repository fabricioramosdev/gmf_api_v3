from fastapi import APIRouter

from .auth import router as router_auth
from .user import router as router_user
from .client import router as router_client

api_v3 = APIRouter(prefix="/v3")


api_v3.include_router(router_client)
api_v3.include_router(router_user)
api_v3.include_router(router_auth)
