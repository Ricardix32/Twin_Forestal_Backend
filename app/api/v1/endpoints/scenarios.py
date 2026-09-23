from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.scenario import Scenario
from app.schemas.scenario import ScenarioResponse

router = APIRouter(prefix="/scenarios", tags=["Scenarios"])

@router.get("", response_model=List[ScenarioResponse])
def get_all_scenarios(db: Session = Depends(get_db)):
    return db.query(Scenario).all()

@router.get("/{scenario_id}", response_model=ScenarioResponse)
def get_scenario_by_id(scenario_id: str, db: Session = Depends(get_db)):
    sc = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not sc:
        raise HTTPException(status_code=404, detail=f"Escenario con id '{scenario_id}' no encontrado")
    return sc
