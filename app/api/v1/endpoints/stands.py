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

@router.get("/geojson/{region_id}")
def get_stands_geojson(region_id: str, db: Session = Depends(get_db)):
    """
    Retorna los rodales de una región en formato estándar GeoJSON FeatureCollection
    para renderizado directo y de alto rendimiento en Leaflet o Mapbox.
    """
    stands = db.query(Stand).filter(Stand.region_id == region_id).all()
    if not stands:
        raise HTTPException(status_code=404, detail=f"No se encontraron rodales para la región '{region_id}'")

    features = []
    for stand in stands:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [stand.lng, stand.lat],
            },
            "properties": {
                "stand_id": stand.stand_id,
                "region_id": stand.region_id,
                "x": stand.x,
                "y": stand.y,
                "species": stand.species,
                "stand_age": stand.stand_age,
                "agb_mgc_ha": stand.agb_mgc_ha,
                "gedi_height_m": stand.gedi_height_m,
                "ndvi": stand.ndvi,
                "ndwi": stand.ndwi,
                "fuel_moisture_pct": stand.fuel_moisture_pct,
                "fwi_risk": stand.fwi_risk,
                "soc_mgc_ha": stand.soc_mgc_ha,
                "gpp_flux": stand.gpp_flux,
                "nee_flux": stand.nee_flux,
                "reco_flux": stand.reco_flux,
                "slope_pct": stand.slope_pct,
                "aspect": stand.aspect,
                "elevation_m": stand.elevation_m,
            },
        })

    return {
        "type": "FeatureCollection",
        "region_id": region_id,
        "total_features": len(features),
        "features": features,
    }

@router.get("/{stand_id}", response_model=StandResponse, response_model_by_alias=True)
def get_stand_by_id(stand_id: str, db: Session = Depends(get_db)):
    stand = db.query(Stand).filter(Stand.stand_id == stand_id).first()
    if not stand:
        raise HTTPException(status_code=404, detail=f"Rodal con stand_id '{stand_id}' no encontrado")
    return stand
