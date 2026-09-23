from typing import List, Optional
from pydantic import BaseModel, Field

class Simulation3PGRequest(BaseModel):
    species: str = "pine"
    years: int = Field(default=30, ge=1, le=100)
    thinning: float = Field(default=0.0, ge=0.0, le=100.0)
    prescribedBurn: bool = Field(default=False)
    droughtSeverity: float = Field(default=1.0, ge=0.5, le=3.0)

class Simulation3PGResultItem(BaseModel):
    year: int
    agb: float
    soc: float
    totalCarbon: float
    lai: float
    npp: float
    gpp: float
    nee: float
    fireRisk: float
    stemDensity: int

class Simulation3PGResponse(BaseModel):
    results: List[Simulation3PGResultItem]
