from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

class ModelMetricItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    model_name: str = Field(..., alias="modelName")
    model_type: str = Field(..., alias="modelType")
    r2: float
    rmse: float
    mae: float
    description: str

class UncertaintyDistributionItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    method: str
    sigma_error_mgc_ha: float = Field(..., alias="sigmaErrorMgCHa")
    ci_95_pct_mgc_ha: float = Field(..., alias="ci95PctMgCHa")
    reduction_pct: float = Field(..., alias="reductionPct")
    status: str

class ScenarioTradeoffItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    scenario_name: str = Field(..., alias="scenarioName")
    fire_risk_cumulative_50yr_pct: float = Field(..., alias="fireRiskCumulative50yrPct")
    carbon_retention_50yr_pct: float = Field(..., alias="carbonRetention50yrPct")
    net_carbon_gain_rate: float = Field(..., alias="netCarbonGainRate")
    resilience_category: str = Field(..., alias="resilienceCategory")

class DensityPoint(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    x: float
    traditional: float
    single_sensor: float = Field(..., alias="singleSensor")
    multiscale_fusion: float = Field(..., alias="multiscaleFusion")

class ScientificMetricsResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    framework: str
    paper_title: str = Field(..., alias="paperTitle")
    main_hypothesis: Dict[str, Any] = Field(..., alias="mainHypothesis")
    hypotheses: Dict[str, Any]
    model_comparison: List[ModelMetricItem] = Field(..., alias="modelComparison")
    uncertainty_distributions: List[UncertaintyDistributionItem] = Field(..., alias="uncertaintyDistributions")
    scenario_tradeoffs: List[ScenarioTradeoffItem] = Field(..., alias="scenarioTradeoffs")
    distribution_curves: List[DensityPoint] = Field(..., alias="distributionCurves")
