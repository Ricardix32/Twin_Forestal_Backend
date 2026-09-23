from pydantic import BaseModel, Field, ConfigDict

class FluxTimeSeriesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    region_id: str
    month: str
    timestamp: str
    tempC: float = Field(validation_alias="temp_c", serialization_alias="tempC")
    precipMm: float = Field(validation_alias="precip_mm", serialization_alias="precipMm")
    vpdKPa: float = Field(validation_alias="vpd_kpa", serialization_alias="vpdKPa")
    radMJm2: float = Field(validation_alias="rad_mj_m2", serialization_alias="radMJm2")
    pg3_gpp: float
    pg3_nee: float
    pg3_reco: float
    pg3_agb: float
    hybrid_gpp: float
    hybrid_nee: float
    hybrid_reco: float
    hybrid_ci_upper: float
    hybrid_ci_lower: float
    fluxnet_gpp: float
    fluxnet_nee: float
    fluxnet_reco: float
