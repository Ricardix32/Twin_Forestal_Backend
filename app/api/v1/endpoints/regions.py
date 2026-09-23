from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.region import Region
from app.schemas.region import RegionResponse

router = APIRouter(prefix="/regions", tags=["Regions"])

@router.get("", response_model=List[RegionResponse])
def get_all_regions(db: Session = Depends(get_db)):
    regions = db.query(Region).all()
    return [RegionResponse.from_orm_with_center(r) for r in regions]

@router.get("/{region_id}", response_model=RegionResponse)
def get_region_by_id(region_id: str, db: Session = Depends(get_db)):
    region = db.query(Region).filter(Region.id == region_id).first()
    if not region:
        raise HTTPException(status_code=404, detail=f"Región con id '{region_id}' no encontrada")
    return RegionResponse.from_orm_with_center(region)
