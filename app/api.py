from fastapi import APIRouter

from app.insurance.views import router as insurance_router
from app.tariff.views import router as tariffs_router

api_router = APIRouter()

api_router.include_router(insurance_router, prefix="/insurance", tags=["insurance"])
api_router.include_router(tariffs_router, prefix="/tariffs", tags=["tariffs"])


@api_router.get("/healthcheck", include_in_schema=False)
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
