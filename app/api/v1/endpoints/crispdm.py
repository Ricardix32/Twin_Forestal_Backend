from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.crispdm_service import CrispDmService
from app.services.semantic_twin import (
    StandTelemetryInput,
    SemanticDecisionOutput,
    run_semantic_evaluation,
    get_langflow_flow_schema,
)

router = APIRouter(prefix="/crisp-dm", tags=["CRISP-DM Methodology"])

@router.get("/overview")
def get_crispdm_overview(
    region_id: Optional[str] = Query(default="madre-de-dios-peru", description="ID del paisaje de estudio"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Retorna el estado de las 6 fases de la metodología CRISP-DM adaptadas al Gemelo Digital
    calculadas en tiempo real a partir del estado de la base de datos y de las fuentes disponibles.
    """
    return CrispDmService.get_full_overview(db, region_id)

@router.post("/phase/{phase_id}/run")
def run_crispdm_phase_action(
    phase_id: str,
    payload: Dict[str, Any] = Body(default={}),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Ejecuta la acción o diagnóstico correspondiente a una de las 6 fases de CRISP-DM.
    """
    return CrispDmService.run_phase_action(phase_id, payload, db)

@router.get("/langflow-flow")
def get_crispdm_langflow_flow() -> Dict[str, Any]:
    """
    Devuelve la especificación de grafo exportable en formato Langflow (JSON)
    para el flujo semántico del gemelo digital (Fase 6 de CRISP-DM).
    """
    return get_langflow_flow_schema()

@router.post("/semantic-evaluation", response_model=SemanticDecisionOutput)
def evaluate_semantic_stand(input_data: StandTelemetryInput):
    """
    Ejecuta la cadena semántica LangChain (Dao et al., 2025) sobre la telemetría de un rodal.
    """
    return run_semantic_evaluation(input_data)
