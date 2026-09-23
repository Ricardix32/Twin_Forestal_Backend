"""
Servicio de Gemelo Digital Semántico (Semantic Digital Twin)
Basado en Dao et al. (2025) y orquestado mediante LangChain.
Transforma telemetría forestal heterogénea (LiDAR GEDI, Sentinel-1/2, FWI, 3-PG)
en inferencias estructuradas de alerta temprana y soporte a la toma de decisiones silvícolas.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

class StandTelemetryInput(BaseModel):
    stand_id: str = Field(default="STAND-TAM-0101", description="Identificador del rodal")
    region_name: str = Field(default="Reserva Nacional Tambopata", description="Nombre del paisaje de estudio")
    species: str = Field(default="Dipteryx micrantha", description="Especie forestal dominante")
    agb_mgc_ha: float = Field(default=245.0, description="Biomasa aérea (Mg C/ha)")
    gedi_height_m: float = Field(default=32.5, description="Altura del dosel RH98 por LiDAR GEDI (m)")
    fuel_moisture_pct: float = Field(default=24.0, description="Humedad de combustible vivo por Sentinel-1 SAR (%)")
    fwi_risk: float = Field(default=0.72, description="Probabilidad de riesgo FWI [0.0 - 1.0]")
    ndvi: float = Field(default=0.78, description="Vigor fotosintético Sentinel-2 NDVI")
    slope_pct: float = Field(default=18.0, description="Pendiente del terreno (%)")
    days_without_rain: int = Field(default=22, description="Días consecutivos sin precipitación efectiva")

class SemanticDecisionOutput(BaseModel):
    stand_id: str
    risk_level: str
    fire_behavior: str
    adaptive_intervention: str
    carbon_tradeoff_assessment: str
    uncertainty_ci_width: float
    scientific_basis: str
    flow_step: str

def build_langchain_semantic_chain():
    """
    Construye la cadena semántica usando LangChain Expression Language (LCEL).
    """
    try:
        from langchain_core.prompts import PromptTemplate
        from langchain_core.runnables import RunnableLambda

        def evaluate_heuristics(telemetry: Dict[str, Any]) -> Dict[str, Any]:
            fwi = telemetry.get("fwi_risk", 0.5)
            fmc = telemetry.get("fuel_moisture_pct", 30.0)
            height = telemetry.get("gedi_height_m", 25.0)
            agb = telemetry.get("agb_mgc_ha", 150.0)
            slope = telemetry.get("slope_pct", 10.0)

            # Clasificación de riesgo basada en FWI + Van Wagner
            if fwi >= 0.70 or fmc < 20.0:
                risk = "EXTREMO (Alerta Roja)"
                behavior = (
                    f"Riesgo crítico de fuego de copa activo. Altura de dosel ({height}m) con combustible "
                    f"desecado (<20%). Propagación acelerada por pendiente ({slope}%)."
                )
                intervention = (
                    "Intervención de emergencia: Quema prescrita perimetral de baja intensidad en faja de 30m "
                    "y apertura inmediata de cortafuegos para fragmentar la continuidad horizontal del combustible."
                )
                carbon_impact = (
                    f"Evita pérdida catastrófica del 85% del stock de AGB ({agb} Mg C/ha). Sacrificio de combustible "
                    "fino superficial estimado en <4% del carbono total."
                )
            elif fwi >= 0.45 or fmc < 40.0:
                risk = "MODERADO - ALTO (Alerta Amarilla)"
                behavior = (
                    "Fuego de superficie con probabilidad de transición a copas aisladas (torching). "
                    "Humedad foliar comprometida."
                )
                intervention = (
                    "Manejo adaptativo planificado: Clareo selectivo de masa intermedia (20-25% de área basal) "
                    "para elevar la altura de base de copa (CBH) y reducir estrés hídrico por competencia."
                )
                carbon_impact = (
                    "Estabiliza el stock a 50 años. Incrementa resiliencia hídrica del rodal con ganancia neta en fustes dominantes."
                )
            else:
                risk = "BAJO - CONDICIONES ÓPTIMAS (Monitoreo Continuo)"
                behavior = "Bajo potencial de ignición. Humedad de combustible suficiente para sofocar focos incipientes."
                intervention = (
                    "Conservación estricta y enriquecimiento forestal con especies autóctonas de alta densidad de madera (e.g. Bertholletia excelsa)."
                )
                carbon_impact = (
                    f"Secuestro neto activo: Tasa proyectada de +3.2 Mg C/ha/año con sumidero de suelo estable."
                )

            return {
                "stand_id": telemetry.get("stand_id", "STAND-UNKNOWN"),
                "risk_level": risk,
                "fire_behavior": behavior,
                "adaptive_intervention": intervention,
                "carbon_tradeoff_assessment": carbon_impact,
                "uncertainty_ci_width": round(18.5 + (fwi * 4.2), 2),
                "scientific_basis": "Dao et al. (2025) [Semantic Digital Twins] + Aragoneses et al. (2024) [LiDAR Fuels] + 3-PG",
                "flow_step": "LangChain Runnable Execution (Telemetry -> Ecological Rules -> Adaptive Management)",
            }

        chain = RunnableLambda(evaluate_heuristics)
        return chain
    except ImportError:
        logger.warning("LangChain core not installed, running native fallback engine.")
        return None

def run_semantic_evaluation(input_data: StandTelemetryInput) -> SemanticDecisionOutput:
    """
    Ejecuta el pipeline semántico de decisión para el rodal.
    """
    raw_dict = input_data.model_dump()
    chain = build_langchain_semantic_chain()

    if chain:
        try:
            # Invocar cadena de LangChain
            res = chain.invoke(raw_dict)
            return SemanticDecisionOutput(**res)
        except Exception as e:
            logger.error(f"Error invoking LangChain chain: {e}")

    # Fallback determinístico con la misma taxonomía de Dao et al. (2025)
    fwi = input_data.fwi_risk
    if fwi >= 0.70:
        risk = "EXTREMO (Alerta Roja)"
        behavior = f"Riesgo de transición a fuego de copa. Dosel GEDI {input_data.gedi_height_m}m con desecación."
        intervention = "Quema prescrita perimetral y apertura de fajas cortafuegos (Manejo Adaptativo de Emergencia)."
        impact = f"Preserva el 85% de la biomasa ({input_data.agb_mgc_ha} Mg C/ha) ante incendio no controlado."
    else:
        risk = "MODERADO / BAJO (Alerta Verde)"
        behavior = "Fuego superficial controlado; humedad foliar adecuada."
        intervention = "Clareo preventivo de baja intensidad y monitoreo satelital quincenal."
        impact = "Crecimiento sostenido con sumidero de carbono positivo."

    return SemanticDecisionOutput(
        stand_id=input_data.stand_id,
        risk_level=risk,
        fire_behavior=behavior,
        adaptive_intervention=intervention,
        carbon_tradeoff_assessment=impact,
        uncertainty_ci_width=18.5,
        scientific_basis="Dao et al. (2025); Aragoneses et al. (2024); Mõttus et al. (2021)",
        flow_step="Native Semantic Fallback",
    )

def get_langflow_flow_schema() -> Dict[str, Any]:
    """
    Devuelve la especificación JSON exportada del flujo visual de Langflow
    para orquestar el Gemelo Digital Forestal Semántico.
    Compatible con Langflow 1.0+ y visualizable en el componente React.
    """
    return {
        "name": "SilvaTwin Semantic Decision Engine",
        "description": "Flujo Langflow para asimilar telemetría forestal y generar directivas de manejo adaptativo.",
        "nodes": [
            {
                "id": "node_satellite_telemetry",
                "type": "CustomComponent",
                "label": "Telemetría Multi-Sensor (Sentinel-1/2 + GEDI)",
                "data": {
                    "source": "NASA GEDI L4A + Copernicus Sentinel-1/2",
                    "features": ["NDVI", "NDWI", "RH98", "SAR_ratio", "FWI"],
                    "frequency": "Mensual a Quincenal",
                },
                "position": {"x": 50, "y": 150},
            },
            {
                "id": "node_3pg_ecophysiology",
                "type": "ProcessModel",
                "label": "Motor Biofísico 3-PG",
                "data": {
                    "model": "Landsberg & Waring (1997)",
                    "outputs": ["GPP", "NPP", "Partición Raíz/Fuste", "Transpiración"],
                },
                "position": {"x": 350, "y": 80},
            },
            {
                "id": "node_wildfire_engine",
                "type": "RiskModel",
                "label": "Modelo de Combustible & Fuego",
                "data": {
                    "formulation": "Canadian FWI + Rothermel + Van Wagner",
                    "outputs": ["Probabilidad de Copa", "Longitud de Llama", "ROS"],
                },
                "position": {"x": 350, "y": 240},
            },
            {
                "id": "node_langchain_agent",
                "type": "LangChainAgent",
                "label": "Agente Semántico Dao et al. (2025)",
                "data": {
                    "framework": "LangChain LCEL",
                    "role": "Evaluador de disyuntivas Carbono vs. Riesgo de Fuego",
                },
                "position": {"x": 680, "y": 160},
            },
            {
                "id": "node_action_output",
                "type": "OutputDecision",
                "label": "Recomendación de Manejo Adaptativo",
                "data": {
                    "actions": ["Clareo Selectivo", "Quema Prescrita", "Restauración"],
                    "kpi": "Reducción de Incertidumbre >= 30%",
                },
                "position": {"x": 980, "y": 160},
            },
        ],
        "edges": [
            {"id": "e1", "source": "node_satellite_telemetry", "target": "node_3pg_ecophysiology"},
            {"id": "e2", "source": "node_satellite_telemetry", "target": "node_wildfire_engine"},
            {"id": "e3", "source": "node_3pg_ecophysiology", "target": "node_langchain_agent"},
            {"id": "e4", "source": "node_wildfire_engine", "target": "node_langchain_agent"},
            {"id": "e5", "source": "node_langchain_agent", "target": "node_action_output"},
        ],
    }
