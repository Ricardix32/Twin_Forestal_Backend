from fastapi import APIRouter
from app.schemas.ai import AIAdvisorRequest, AIAdvisorResponse
from app.services.ai_advisor import get_ai_advice

router = APIRouter(prefix="/ai-advisor", tags=["AI Advisor"])

@router.post("", response_model=AIAdvisorResponse)
async def ai_advisor_endpoint(req: AIAdvisorRequest):
    return await get_ai_advice(req)
