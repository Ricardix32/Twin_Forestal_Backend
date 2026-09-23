from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.timeseries import FluxTimeSeries
from app.schemas.timeseries import FluxTimeSeriesResponse
from app.schemas.simulation import Simulation3PGRequest, Simulation3PGResponse
from app.services.simulator import run_3pg_simulation

router = APIRouter(prefix="/simulations", tags=["Simulations"])

@router.post("/3pg", response_model=Simulation3PGResponse)
def simulate_3pg_endpoint(req: Simulation3PGRequest):
    results = run_3pg_simulation(req)
    return Simulation3PGResponse(results=results)

@router.get("/flux-timeseries/{region_id}", response_model=List[FluxTimeSeriesResponse])
def get_flux_timeseries(region_id: str, db: Session = Depends(get_db)):
    series = db.query(FluxTimeSeries).filter(FluxTimeSeries.region_id == region_id).all()
    if not series:
        # Check if there is global/default series if specific region series is empty
        series = db.query(FluxTimeSeries).all()
    return series
