from typing import Any, Dict, Optional
from pydantic import BaseModel

class AIAdvisorRequest(BaseModel):
    prompt: str
    context: Optional[Dict[str, Any]] = None

class AIAdvisorResponse(BaseModel):
    response: str
