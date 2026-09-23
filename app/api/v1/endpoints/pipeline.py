from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.pipeline_service import scan_data_directory, execute_pipeline

router = APIRouter(prefix="/pipeline", tags=["Data Pipeline"])

class RunPipelineRequest(BaseModel):
    regionId: str = "madre-de-dios-peru"

@router.get("/status")
def get_pipeline_status() -> Dict[str, Any]:
    """
    Returns scan of data/ directory showing detected datasets, file counts and formats.
    """
    return scan_data_directory()

@router.post("/run")
def run_ingest_pipeline(req: RunPipelineRequest, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Executes ingestion and processing pipeline for GEDI H5, Sentinel-2 TIF, etc.
    """
    return execute_pipeline(req.regionId, db)
