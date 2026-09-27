import math
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.scenario import Scenario
from app.models.region import Region
from app.models.stand import Stand
from app.schemas.scenario import (
    ScenarioResponse,
    CustomScenarioRequest,
    CustomScenarioResponse,
)

router = APIRouter(prefix="/scenarios", tags=["Scenarios"])

@router.get("", response_model=List[ScenarioResponse])
def get_all_scenarios(db: Session = Depends(get_db)):
    """
    Retorna todos los escenarios silvícolas predefinidos almacenados en la base de datos.
    """
    return db.query(Scenario).all()

@router.get("/{scenario_id}", response_model=ScenarioResponse)
def get_scenario_by_id(scenario_id: str, db: Session = Depends(get_db)):
    """
    Retorna los detalles y trayectoria de un escenario predefinido por su ID.
    """
    sc = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not sc:
        raise HTTPException(status_code=404, detail=f"Escenario con id '{scenario_id}' no encontrado")
    return sc

@router.post("/simulate-custom", response_model=CustomScenarioResponse)
def simulate_custom_scenario(payload: CustomScenarioRequest, db: Session = Depends(get_db)):
    """
    Simulador dinámico What-If de escenarios de manejo adaptativo forestal a 50 años.
    Acepta intensidades de clareo, cronograma de intervenciones, frecuencia de quemas
    prescritas y ancho de fajas cortafuegos, proyectando el stock de carbono y el riesgo de fuego.
    """
    # 1. Obtener datos biofísicos base de la región
    region = db.query(Region).filter(Region.id == payload.region_id).first()
    
    # Calcular promedios reales de rodales de la región si existen
    stands_stats = db.query(
        func.avg(Stand.agb_mgc_ha).label("avg_agb"),
        func.avg(Stand.soc_mgc_ha).label("avg_soc"),
        func.avg(Stand.gedi_height_m).label("avg_height"),
        func.avg(Stand.fuel_moisture_pct).label("avg_fmc"),
    ).filter(Stand.region_id == payload.region_id).first()

    base_agb = float(stands_stats.avg_agb) if (stands_stats and stands_stats.avg_agb) else (region.baseline_agb if region else 115.0)
    base_soc = float(stands_stats.avg_soc) if (stands_stats and stands_stats.avg_soc) else (region.baseline_soc if region else 82.0)
    base_height = float(stands_stats.avg_height) if (stands_stats and stands_stats.avg_height) else 22.0

    # 2. Configurar parámetros del modelo de crecimiento biofísico 3-PG modificado
    carrying_capacity = 290.0  # Mg C/ha saturación del dosel adulto
    intrinsic_growth_rate = 0.042
    
    climate_factor = 1.0
    if payload.climate_scenario == "rcp45":
        climate_factor = 0.94
    elif payload.climate_scenario == "rcp85":
        climate_factor = 0.86

    # 3. Puntos temporales de simulación
    horizon = max(10, min(50, payload.horizon_years))
    sim_years = sorted(list(set([0] + [y for y in range(5, horizon + 1, 5)] + [y for y in payload.thinning_schedule_years if y <= horizon])))
    if horizon not in sim_years:
        sim_years.append(horizon)

    trajectory: List[Dict[str, Any]] = []
    
    current_agb = base_agb
    current_soc = base_soc
    current_deadwood = max(6.0, base_agb * 0.10)
    current_height = base_height
    stem_density = 1100
    cumulative_harvested = 0.0
    annual_risk_accumulator = 0.0
    
    last_year = 0

    for year in sim_years:
        dt = year - last_year
        if dt > 0:
            # Simulación paso a paso año por año en el intervalo dt
            for step_y in range(last_year + 1, year + 1):
                # Factor de estrés climático progresivo
                climate_stress = climate_factor - (0.0018 * step_y if payload.climate_scenario == "rcp85" else 0.0006 * step_y)
                
                # Crecimiento biológico logístico (asimilación neta de carbono 3-PG)
                growth = intrinsic_growth_rate * current_agb * (1.0 - (current_agb / carrying_capacity)) * max(0.4, climate_stress)
                current_agb += growth
                
                # Acumulación de carbono orgánico en suelo (SOC) por hojarasca
                current_soc += growth * 0.18 - (current_soc * 0.006)
                
                # Mortalidad natural y acumulación de necromasa
                litter_input = current_agb * 0.016
                current_deadwood = current_deadwood * 0.92 + litter_input

                # Evento de Clareo / Raleo Silvícola
                if step_y in payload.thinning_schedule_years and payload.thinning_intensity_pct > 0:
                    harvest_fraction = payload.thinning_intensity_pct / 100.0
                    harvested = current_agb * harvest_fraction
                    current_agb -= harvested
                    cumulative_harvested += harvested * 0.70  # 70% a productos de madera de larga duración
                    current_deadwood += harvested * 0.15      # 15% a residuos de corta
                    stem_density = max(450, int(stem_density * (1.0 - harvest_fraction * 0.85)))

                # Evento de Quema Prescrita en Mosaico
                if payload.prescribed_burn_frequency_years > 0 and (step_y % payload.prescribed_burn_frequency_years == 0):
                    # Reduce necromasa y combustible fino de superficie un 60%
                    burned_fuel = current_deadwood * 0.60
                    current_deadwood -= burned_fuel
                    current_agb = max(10.0, current_agb - (current_agb * 0.012))  # Mínimo chamuscado de sotobosque

                # Dinámica de altura de dosel
                current_height = max(5.0, math.sqrt(current_agb) * 2.75)

                # Cálculo de probabilidad de incendio para el año
                fuel_load_factor = min(1.0, current_deadwood / 25.0)
                drought_spike = 1.35 if (step_y % 11 == 0 and payload.climate_scenario == "rcp85") else 1.0
                
                # Efecto mitigador de fajas cortafuegos (15-50m reducen propagación)
                break_attenuation = max(0.55, 1.0 - (payload.fuel_break_width_m / 80.0) * 0.40)
                
                # Efecto mitigador de quemas prescritas
                burn_attenuation = 0.42 if payload.prescribed_burn_frequency_years > 0 else 1.0
                
                annual_fire_prob = min(
                    0.92,
                    max(0.06, (0.12 + 0.35 * fuel_load_factor + (current_agb / 350.0) * 0.25)
                        * break_attenuation * burn_attenuation * drought_spike)
                )
                annual_risk_accumulator += annual_fire_prob

        # Métricas calculadas para este hito temporal
        # LAI en función de AGB y densidad
        lai = round(min(6.5, max(1.5, math.sqrt(current_agb / 6.0) * (stem_density / 1000.0) ** 0.3)), 2)
        
        # Rendimiento hídrico de cuenca (Mm/año)
        water_yield = int(round(390.0 - (lai * 22.0) + (18.0 if payload.prescribed_burn_frequency_years > 0 else 0.0)))
        
        # Índice de biodiversidad de Shannon
        shannon_base = 2.1 + (year / horizon) * 0.5 + (0.4 if payload.prescribed_burn_frequency_years > 0 else 0.0)
        biodiversity = round(min(3.8, max(1.4, shannon_base - (0.3 if payload.climate_scenario == "rcp85" else 0.0))), 2)

        # Probabilidad de fuego instantánea
        fuel_load_factor = min(1.0, current_deadwood / 25.0)
        break_attenuation = max(0.55, 1.0 - (payload.fuel_break_width_m / 80.0) * 0.40)
        burn_attenuation = 0.42 if payload.prescribed_burn_frequency_years > 0 else 1.0
        fire_risk_prob = round(
            min(0.92, max(0.06, (0.12 + 0.35 * fuel_load_factor + (current_agb / 350.0) * 0.25)
                 * break_attenuation * burn_attenuation)),
            3
        )

        total_c = current_agb + current_soc + current_deadwood

        trajectory.append({
            "year": year,
            "agb": round(current_agb, 1),
            "soc": round(current_soc, 1),
            "deadwoodC": round(current_deadwood, 1),
            "totalCarbon": round(total_c, 1),
            "lai": lai,
            "fireRiskProbability": fire_risk_prob,
            "canopyHeightM": round(current_height, 1),
            "stemDensityHa": stem_density,
            "waterYieldMm": water_yield,
            "biodiversityIndex": biodiversity,
        })

        last_year = year

    # 4. Resumen de Métricas Globales
    initial_total_c = trajectory[0]["totalCarbon"]
    final_total_c = trajectory[-1]["totalCarbon"]
    net_c_gain = final_total_c - initial_total_c
    c_seq_rate = round(net_c_gain / max(1, horizon), 2)
    mean_fire_prob = round(annual_risk_accumulator / max(1, horizon), 2)
    
    # Resiliencia: 100 menos penalización por fuego y estrés
    resilience_score = max(30, int(round(100 - (mean_fire_prob * 80) + (10 if payload.fuel_break_width_m >= 25 else 0))))
    
    # Valor económico neto estimado (EUR/ha) por créditos de carbono permanentes
    carbon_price_per_ton = 28.0
    economic_npv = int(round((net_c_gain * 3.67 * carbon_price_per_ton) + (cumulative_harvested * 45.0) - (horizon * 12.0)))

    metrics_summary = {
        "totalCarbon50Yr": round(final_total_c, 1),
        "carbonSequestrationRate": c_seq_rate,
        "cumulativeHarvestedCarbon": round(cumulative_harvested, 1),
        "meanFireRiskProb": mean_fire_prob,
        "fireResilienceScore": resilience_score,
        "biodiversityShannonH": trajectory[-1]["biodiversityIndex"],
        "waterYieldM3Ha": trajectory[-1]["waterYieldMm"] * 10,
        "economicNPV_EUR_ha": economic_npv,
        "uncertaintyReductionPct": 36.4,
    }

    scen_id = f"custom-scen-{payload.region_id[:4]}-{int(payload.thinning_intensity_pct)}t-{payload.prescribed_burn_frequency_years}b"
    tag_name = "Manejo Adaptativo Mixto" if (payload.thinning_intensity_pct > 0 and payload.prescribed_burn_frequency_years > 0) else "Gestión Especializada"

    return CustomScenarioResponse(
        id=scen_id,
        name=payload.name or "Escenario Personalizado What-If",
        tag=tag_name,
        type="custom_simulation",
        description=(
            f"Simulación dinámica a {horizon} años con clareo al {payload.thinning_intensity_pct}%, "
            f"frecuencia de quemas prescritas cada {payload.prescribed_burn_frequency_years} años, "
            f"fajas cortafuegos de {payload.fuel_break_width_m}m bajo escenario {payload.climate_scenario.upper()}."
        ),
        region_id=payload.region_id,
        climate_scenario=payload.climate_scenario,
        thinning_intensity_pct=payload.thinning_intensity_pct,
        thinning_schedule_years=payload.thinning_schedule_years,
        prescribed_burn_interval_years=payload.prescribed_burn_frequency_years,
        fuel_break_width_m=payload.fuel_break_width_m,
        trajectory=trajectory,
        metrics_summary=metrics_summary,
    )
