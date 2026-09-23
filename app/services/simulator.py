import math
from typing import List
from app.schemas.simulation import Simulation3PGRequest, Simulation3PGResultItem

def run_3pg_simulation(req: Simulation3PGRequest) -> List[Simulation3PGResultItem]:
    species = req.species.lower()
    years = req.years
    thinning = req.thinning
    prescribed_burn = req.prescribedBurn
    drought_severity = req.droughtSeverity

    if species == "eucalyptus":
        current_agb = 45.0
        current_lai = 3.2
        current_soc = 75.0
        stem_density = 1200
    elif species == "tropical":
        current_agb = 180.0
        current_lai = 5.8
        current_soc = 110.0
        stem_density = 650
    else:  # pine / default
        current_agb = 85.0
        current_lai = 3.8
        current_soc = 75.0
        stem_density = 950

    results = []

    for yr in range(years + 1):
        # Ecophysiological Modifiers
        age_mod = max(0.6, 1.0 - math.exp(-0.08 * (yr + 10)))
        vpd_mod = max(0.4, 1.0 - (drought_severity - 1.0) * 0.35)
        temp_mod = 0.92
        gpp_efficiency = 0.045 * age_mod * vpd_mod * temp_mod

        apar = 1200.0 * (1.0 - math.exp(-0.5 * current_lai))
        annual_npp = apar * gpp_efficiency * 0.47

        # Carbon allocation fractions
        eta_roots = 0.25 + (1.0 - vpd_mod) * 0.15
        eta_foliage = 0.22
        eta_stem = max(0.1, 1.0 - eta_roots - eta_foliage)

        # Forest Management Interventions
        if yr == 5 and thinning > 0:
            thin_frac = thinning / 100.0
            current_agb *= (1.0 - thin_frac)
            stem_density = round(stem_density * (1.0 - thin_frac))
            current_lai *= (1.0 - thin_frac * 0.7)

        if yr == 10 and prescribed_burn:
            current_soc *= 0.96

        # Growth & turnover
        current_agb += (annual_npp * eta_stem) - (current_agb * 0.015)
        current_soc += (annual_npp * (eta_roots + eta_foliage) * 0.3) - (current_soc * 0.018)
        current_lai = min(6.5, current_lai + (annual_npp * eta_foliage * 0.18) - (current_lai * 0.12))

        # Wildfire risk estimation
        cyclical_drop = 15.0 if yr % 4 == 0 else 0.0
        fuel_moisture = max(12.0, 65.0 - (drought_severity - 1.0) * 35.0 - cyclical_drop)
        burn_mitigation = 0.25 if (prescribed_burn and 10 <= yr <= 18) else 0.0
        raw_risk = current_agb * 0.003 + (100.0 - fuel_moisture) * 0.008 - burn_mitigation
        fire_risk = min(0.95, max(0.05, raw_risk))

        results.append(
            Simulation3PGResultItem(
                year=yr,
                agb=round(current_agb, 2),
                soc=round(current_soc, 2),
                totalCarbon=round(current_agb + current_soc, 2),
                lai=round(current_lai, 2),
                npp=round(annual_npp, 2),
                gpp=round(annual_npp / 0.47, 2),
                nee=round(-annual_npp * 0.75, 2),
                fireRisk=round(fire_risk, 3),
                stemDensity=int(stem_density),
            )
        )

    return results
