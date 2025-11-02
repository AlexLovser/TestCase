from fastapi import APIRouter
from .address import router as address_router
from .enterprise import router as enterprise_router
from .domain import router as domain_router


api_router = APIRouter(prefix="/api")
api_router.include_router(address_router)
api_router.include_router(enterprise_router)
api_router.include_router(domain_router)

__all__ = ["api_router"]
