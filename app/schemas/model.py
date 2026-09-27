from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict, model_validator

class AGBPredictRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    rh98_m: float = Field(default=25.0, ge=0.0, le=70.0, description="Altura de dosel LiDAR GEDI RH98 en metros")
    ndvi: float = Field(default=0.75, ge=-1.0, le=1.0, description="Índice de Vegetación Sentinel-2 NDVI")
    savi: float = Field(default=0.60, ge=-1.0, le=1.0, description="Soil Adjusted Vegetation Index")
    ndwi: float = Field(default=0.30, ge=-1.0, le=1.0, description="Índice de Agua / Humedad NDWI")
    fmc_pct: float = Field(default=80.0, ge=0.0, le=150.0, description="Humedad de combustible foliar derivado de Sentinel-1 SAR (%)")
    vpd_kpa: float = Field(default=1.20, ge=0.0, le=6.0, description="Déficit de presión de vapor atmosférico (kPa)")

    @model_validator(mode="before")
    @classmethod
    def handle_camel_case_inputs(cls, values: Any) -> Any:
        if isinstance(values, dict):
            if "rh98M" in values and "rh98_m" not in values:
                values["rh98_m"] = values["rh98M"]
            if "fmcPct" in values and "fmc_pct" not in values:
                values["fmc_pct"] = values["fmcPct"]
            if "vpdKpa" in values and "vpd_kpa" not in values:
                values["vpd_kpa"] = values["vpdKpa"]
        return values

class AGBPredictResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    # Standard snake_case fields matching research contract
    agb_pred_mgc_ha: float
    pure_3pg_estimate_mgc_ha: float
    hybrid_residual_correction: float
    ci_95_lower: float
    ci_95_upper: float
    model_version: str
    scientific_basis: str
    input_parameters: Dict[str, float]

    # Optional camelCase fields for seamless frontend access
    agbPredMgCHa: Optional[float] = None
    pure3pgEstimateMgCHa: Optional[float] = None
    hybridResidualCorrection: Optional[float] = None
    ci95Lower: Optional[float] = None
    ci95Upper: Optional[float] = None
    modelVersion: Optional[str] = None
    scientificBasis: Optional[str] = None

class ModelInfoResponse(BaseModel):
    model_name: str
    architecture: str
    r2: float
    rmse: float
    mae: float
    features: List[str]
    trained_samples: int
    scientific_citations: List[str]
