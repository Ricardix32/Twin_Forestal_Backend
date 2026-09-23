from pydantic import BaseModel, Field, ConfigDict

class StandResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    x: int
    y: int
    lat: float
    lng: float
    standId: str = Field(validation_alias="stand_id", serialization_alias="standId")
    species: str
    standAge: int = Field(validation_alias="stand_age", serialization_alias="standAge")
    agbMgC_ha: float = Field(validation_alias="agb_mgc_ha", serialization_alias="agbMgC_ha")
    gediHeightM: float = Field(validation_alias="gedi_height_m", serialization_alias="gediHeightM")
    ndvi: float
    ndwi: float
    fuelMoisturePct: float = Field(validation_alias="fuel_moisture_pct", serialization_alias="fuelMoisturePct")
    fwiRisk: float = Field(validation_alias="fwi_risk", serialization_alias="fwiRisk")
    socMgC_ha: float = Field(validation_alias="soc_mgc_ha", serialization_alias="socMgC_ha")
    gppFlux: float = Field(validation_alias="gpp_flux", serialization_alias="gppFlux")
    neeFlux: float = Field(validation_alias="nee_flux", serialization_alias="neeFlux")
    recoFlux: float = Field(validation_alias="reco_flux", serialization_alias="recoFlux")
    slopePct: float = Field(validation_alias="slope_pct", serialization_alias="slopePct")
    aspect: str
    elevationM: int = Field(validation_alias="elevation_m", serialization_alias="elevationM")
