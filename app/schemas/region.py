from typing import List, Optional, Tuple
from pydantic import BaseModel, Field

class RegionBase(BaseModel):
    id: str
    name: str
    country: str
    biome: str
    areaHa: float = Field(alias="area_ha")
    dominantSpecies: List[str] = Field(default_factory=list, alias="dominant_species")
    climateType: str = Field(alias="climate_type")
    fluxnetSiteId: Optional[str] = Field(None, alias="fluxnet_site_id")
    fluxnetSiteName: Optional[str] = Field(None, alias="fluxnet_site_name")
    meanAnnualPrecipMm: float = Field(alias="mean_annual_precip_mm")
    meanTempC: float = Field(alias="mean_temp_c")
    elevationM: float = Field(alias="elevation_m")
    baselineAGB: float = Field(alias="baseline_agb")
    baselineSOC: float = Field(alias="baseline_soc")
    description: Optional[str] = None

    class Config:
        populate_by_name = True
        from_attributes = True

class RegionResponse(RegionBase):
    center: Tuple[float, float]

    @classmethod
    def from_orm_with_center(cls, obj):
        return cls(
            id=obj.id,
            name=obj.name,
            country=obj.country,
            biome=obj.biome,
            area_ha=obj.area_ha,
            dominant_species=obj.dominant_species,
            climate_type=obj.climate_type,
            fluxnet_site_id=obj.fluxnet_site_id,
            fluxnet_site_name=obj.fluxnet_site_name,
            mean_annual_precip_mm=obj.mean_annual_precip_mm,
            mean_temp_c=obj.mean_temp_c,
            elevation_m=obj.elevation_m,
            baseline_agb=obj.baseline_agb,
            baseline_soc=obj.baseline_soc,
            description=obj.description,
            center=(obj.lat, obj.lng),
        )
