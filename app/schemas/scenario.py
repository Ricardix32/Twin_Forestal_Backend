from typing import List, Dict, Any
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
