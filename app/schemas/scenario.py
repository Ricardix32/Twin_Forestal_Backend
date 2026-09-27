from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

class ScenarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    name: str
    tag: str
    type: str
    description: str
    thinningIntensityPct: float = Field(validation_alias="thinning_intensity_pct", serialization_alias="thinningIntensityPct")
    thinningScheduleYears: List[int] = Field(validation_alias="thinning_schedule_years", serialization_alias="thinningScheduleYears")
    prescribedBurnIntervalYears: int = Field(validation_alias="prescribed_burn_interval_years", serialization_alias="prescribedBurnIntervalYears")
    reforestationSpecies: str = Field(validation_alias="reforestation_species", serialization_alias="reforestationSpecies")
    fuelBreakWidthM: float = Field(validation_alias="fuel_break_width_m", serialization_alias="fuelBreakWidthM")
    trajectory: List[Dict[str, Any]]
    metricsSummary: Dict[str, Any] = Field(validation_alias="metrics_summary", serialization_alias="metricsSummary")

class CustomScenarioRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    region_id: str = Field(default="madre-de-dios-peru", alias="regionId", description="ID de la región base")
    name: Optional[str] = Field(default="Escenario Personalizado", description="Nombre descriptivo")
    thinning_intensity_pct: float = Field(
        default=15.0, alias="thinningIntensityPct", ge=0.0, le=50.0, description="Intensidad de clareo (%)"
    )
    thinning_schedule_years: List[int] = Field(
        default=[15, 30], alias="thinningScheduleYears", description="Años en que se ejecuta clareo"
    )
    prescribed_burn_frequency_years: int = Field(
        default=5, alias="prescribedBurnFrequencyYears", ge=0, le=20, description="Frecuencia de quemas prescritas (años, 0 = ninguna)"
    )
    fuel_break_width_m: float = Field(
        default=25.0, alias="fuelBreakWidthM", ge=0.0, le=100.0, description="Ancho de fajas cortafuegos (m)"
    )
    horizon_years: int = Field(
        default=50, alias="horizonYears", ge=10, le=50, description="Horizonte temporal de simulación (años)"
    )
    climate_scenario: str = Field(
        default="rcp45", alias="climateScenario", description="Escenario climático de forzamiento: baseline, rcp45, rcp85"
    )

class CustomScenarioResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    tag: str
    type: str
    description: str
    region_id: str = Field(..., alias="regionId")
    climate_scenario: str = Field(..., alias="climateScenario")
    thinning_intensity_pct: float = Field(..., alias="thinningIntensityPct")
    thinning_schedule_years: List[int] = Field(..., alias="thinningScheduleYears")
    prescribed_burn_interval_years: int = Field(..., alias="prescribedBurnIntervalYears")
    fuel_break_width_m: float = Field(..., alias="fuelBreakWidthM")
    trajectory: List[Dict[str, Any]]
    metrics_summary: Dict[str, Any] = Field(..., alias="metricsSummary")
