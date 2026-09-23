from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.stand import Stand
from app.schemas.stand import StandResponse

router = APIRouter(prefix="/stands", tags=["Stands"])

@router.get("/region/{region_id}", response_model=List[StandResponse], response_model_by_alias=True)
def get_stands_by_region(
    region_id: str,
    limit: Optional[int] = Query(default=None, description="Máximo número de rodales a retornar"),
    offset: int = Query(default=0, description="Desplazamiento para paginación"),
    db: Session = Depends(get_db),
):
    query = db.query(Stand).filter(Stand.region_id == region_id).offset(offset)
    if limit is not None:
        query = query.limit(limit)
    stands = query.all()
    return stands

@router.get("/{stand_id}", response_model=StandResponse, response_model_by_alias=True)
def get_stand_by_id(stand_id: str, db: Session = Depends(get_db)):
    stand = db.query(Stand).filter(Stand.stand_id == stand_id).first()
    if not stand:
        raise HTTPException(status_code=404, detail=f"Rodal con stand_id '{stand_id}' no encontrado")
    return stand
