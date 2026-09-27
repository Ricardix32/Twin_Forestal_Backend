from fastapi import APIRouter
from app.api.v1.endpoints.regions import router as regions_router
from app.api.v1.endpoints.stands import router as stands_router
from app.api.v1.endpoints.simulations import router as simulations_router
from app.api.v1.endpoints.scenarios import router as scenarios_router
from app.api.v1.endpoints.ai import router as ai_router
from app.api.v1.endpoints.crispdm import router as crispdm_router
from app.api.v1.endpoints.pipeline import router as pipeline_router
from app.api.v1.endpoints.models import router as models_router
from app.api.v1.endpoints.validation import router as validation_router

api_router = APIRouter()

api_router.include_router(regions_router)
api_router.include_router(stands_router)
api_router.include_router(simulations_router)
api_router.include_router(scenarios_router)
api_router.include_router(ai_router)
api_router.include_router(crispdm_router)
api_router.include_router(pipeline_router)
api_router.include_router(models_router)
api_router.include_router(validation_router)


