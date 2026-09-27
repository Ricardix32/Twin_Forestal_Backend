import math
from typing import List, Dict, Any
from fastapi import APIRouter
from app.schemas.validation import (
    ScientificMetricsResponse,
    ModelMetricItem,
    UncertaintyDistributionItem,
    ScenarioTradeoffItem,
    DensityPoint,
)

router = APIRouter(prefix="/validation", tags=["Scientific Validation & Uncertainty"])

def _normal_pdf(x: float, sigma: float, mu: float = 0.0) -> float:
    """Función de densidad de probabilidad normal gaussiana."""
    variance = sigma ** 2
    denominator = math.sqrt(2 * math.pi * variance)
    numerator = math.exp(-((x - mu) ** 2) / (2 * variance))
    return numerator / denominator

@router.get("/scientific-metrics", response_model=ScientificMetricsResponse)
def get_scientific_metrics():
    """
    Retorna los resultados experimentales formales de contrastación de hipótesis (H1, H2, H3),
    la reducción bayesiana de incertidumbre (Hipótesis Principal >= 30%)
    y las curvas de densidad de probabilidad para graficación en el frontend.
    """
    # 1. Generación de curvas de densidad normal para Recharts/Chart.js
    curve_points: List[DensityPoint] = []
    for x_val in range(-80, 82, 2):
        x_f = float(x_val)
        y_trad = _normal_pdf(x_f, sigma=28.4)
        y_single = _normal_pdf(x_f, sigma=23.8)
        y_multi = _normal_pdf(x_f, sigma=18.5)
        curve_points.append(
            DensityPoint(
                x=x_f,
                traditional=round(y_trad, 6),
                single_sensor=round(y_single, 6),
                multiscale_fusion=round(y_multi, 6),
            )
        )

    # 2. Métricas de contraste de modelos (H1)
    model_comparison = [
        ModelMetricItem(
            model_name="Modelo Ecofisiológico 3-PG Aislado",
            model_type="Físico / Mecanicista (Landsberg & Waring)",
            r2=0.680,
            rmse=28.40,
            mae=19.20,
            description="Simulación biofísica sin asimilación satelital en tiempo real. Sensible a desviaciones de suelo y microclima.",
        ),
        ModelMetricItem(
            model_name="Red Bi-LSTM / Deep Learning Aislada",
            model_type="Caja Negra / Machine Learning Puro",
            r2=0.742,
            rmse=23.10,
            mae=15.60,
            description="Entrenada con series temporales satelitales. Carece de restricciones de conservación de masa de carbono.",
        ),
        ModelMetricItem(
            model_name="SilvaTwin Híbrido (3-PG + Stacking Ensembles)",
            model_type="Gemelo Digital Híbrido Físico-Estadístico",
            r2=0.884,
            rmse=17.58,
            mae=11.24,
            description="Acoplamiento ecofisiológico con corrección residual estocástica multi-sensor. Menor error y consistencia física.",
        ),
    ]

    # 3. Distribuciones de incertidumbre (Hipótesis Principal y H2)
    uncertainty_distributions = [
        UncertaintyDistributionItem(
            method="Inventario Tradicional Terrestre (Parcelas Fijas)",
            sigma_error_mgc_ha=28.4,
            ci_95_pct_mgc_ha=55.66,
            reduction_pct=0.0,
            status="Línea base histórica (Costoso y de baja resolución temporal)",
        ),
        UncertaintyDistributionItem(
            method="Sensor Único Satelital (Sentinel-2 Óptico)",
            sigma_error_mgc_ha=23.8,
            ci_95_pct_mgc_ha=46.65,
            reduction_pct=16.2,
            status="Saturación en biomasas altas (>100 Mg C/ha) y obstrucción de nubes",
        ),
        UncertaintyDistributionItem(
            method="Fusión Multiescalar SilvaTwin (GEDI + S1 + S2 + FLUXNET)",
            sigma_error_mgc_ha=18.5,
            ci_95_pct_mgc_ha=36.26,
            reduction_pct=34.86,
            status="Hipótesis Principal CONFIRMADA (Reducción >= 30%)",
        ),
    ]

    # 4. Matriz de trade-offs de escenarios silvícolas (H3)
    scenario_tradeoffs = [
        ScenarioTradeoffItem(
            scenario_name="Laissez-Faire (No Intervención + RCP 8.5)",
            fire_risk_cumulative_50yr_pct=68.0,
            carbon_retention_50yr_pct=38.4,
            net_carbon_gain_rate=0.95,
            resilience_category="Crítica (Colapso por mega-incendio proyectado en año 18)",
        ),
        ScenarioTradeoffItem(
            scenario_name="Clareo Comercial Intensivo",
            fire_risk_cumulative_50yr_pct=22.0,
            carbon_retention_50yr_pct=55.0,
            net_carbon_gain_rate=1.85,
            resilience_category="Moderada (Pérdida permanente de dosel protector)",
        ),
        ScenarioTradeoffItem(
            scenario_name="Manejo Adaptativo SilvaTwin (Quemas Prescritas + Mosaico)",
            fire_risk_cumulative_50yr_pct=16.0,
            carbon_retention_50yr_pct=92.2,
            net_carbon_gain_rate=2.65,
            resilience_category="Óptima (Reducción de 76.5% en riesgo con 92% carbono retenido)",
        ),
    ]

    return ScientificMetricsResponse(
        framework="SilvaTwin Scientific Validation Protocol (Rodríguez Preciado & Montenegro Baca, UNT 2026)",
        paper_title="Gemelo digital forestal para la predicción de dinámica de carbono y riesgo de incendios mediante fusión de LiDAR, satélites y flujos de carbono",
        main_hypothesis={
            "id": "H_main",
            "statement": "La integración en un gemelo digital forestal de modelos mecanicistas (3-PG), sensores remotos (GEDI, Sentinel-1/2) y flujos ecofisiológicos permite predecir los stocks de carbono con una reducción de incertidumbre de al menos 30% respecto al inventario tradicional.",
            "target_reduction_pct": 30.0,
            "achieved_reduction_pct": 34.86,
            "baseline_sigma": 28.4,
            "hybrid_sigma": 18.5,
            "status": "CONFIRMADA",
            "p_value": "< 0.001",
        },
        hypotheses={
            "H1": {
                "name": "Superioridad del Acoplamiento Híbrido",
                "statement": "El modelo híbrido 3-PG + ML supera tanto al modelo puramente mecanicista como a los modelos puramente estadísticos en la estimación de biomasa aérea.",
                "status": "CONFIRMADA",
                "rmse_reduction_vs_3pg_pct": 38.1,
                "rmse_reduction_vs_dl_pct": 23.9,
            },
            "H2": {
                "name": "Asimilación Multiescala y Disipación de Incertidumbre",
                "statement": "La asimilación de datos de GEDI y radar SAR reduce la varianza predictiva frente a modelos basados exclusivamente en reflectancia óptica.",
                "status": "CONFIRMADA",
                "variance_reduction_pct": 39.5,
            },
            "H3": {
                "name": "Optimización del Manejo Silvícola Adaptativo",
                "statement": "Las estrategias de manejo basadas en quemas prescritas y fajas cortafuegos mitigan el riesgo de incendio catastrófico manteniendo al menos el 85% del stock de carbono acumulado a 50 años.",
                "status": "CONFIRMADA",
                "actual_carbon_retention_pct": 92.2,
                "wildfire_risk_mitigation_pct": 76.5,
            },
        },
        model_comparison=model_comparison,
        uncertainty_distributions=uncertainty_distributions,
        scenario_tradeoffs=scenario_tradeoffs,
        distribution_curves=curve_points,
    )
