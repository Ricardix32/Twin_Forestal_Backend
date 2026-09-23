import math
import logging
from app.core.database import Base, engine, SessionLocal
from app.models.region import Region
from app.models.stand import Stand
from app.models.timeseries import FluxTimeSeries
from app.models.scenario import Scenario

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed")

REGIONS_DATA = [
    {
        "id": "madre-de-dios-peru",
        "name": "Reserva Nacional Tambopata (Madre de Dios)",
        "country": "Perú (Madre de Dios - Amazonía Sur)",
        "biome": "Bosque Tropical Húmedo de Selva Baja",
        "area_ha": 42800.0,
        "lat": -12.825,
        "lng": -69.288,
        "dominant_species": [
            "Cedrela odorata (Cedro de la Selva)",
            "Swietenia macrophylla (Caoba)",
            "Bertholletia excelsa (Castaña del Perú)",
            "Dipteryx micrantha (Shihuahuaco)",
            "Hevea brasiliensis (Shiringa)",
            "Calycophyllum spruceanum (Capirona)",
        ],
        "climate_type": "Tropical superhúmedo megatérmico (Af/Am)",
        "fluxnet_site_id": "PE-Tam / PE-Tambopata",
        "fluxnet_site_name": "Tambopata Megadiverse Permanent Plot",
        "mean_annual_precip_mm": 3150.0,
        "mean_temp_c": 26.4,
        "elevation_m": 210.0,
        "baseline_agb": 268.4,
        "baseline_soc": 142.8,
        "description": "Hotspot de megabiodiversidad global en la Amazonía peruana con presencia dominante de Shihuahuaco, Caoba y Castañales centenarios, sometidos a monitoreo dinámico LiDAR.",
    },
    {
        "id": "bosque-seco-norperuano",
        "name": "Santuario Histórico Bosque de Pómac (Lambayeque)",
        "country": "Perú (Lambayeque / Piura)",
        "biome": "Bosque Seco Tropical Équatorial",
        "area_ha": 15800.0,
        "lat": -6.475,
        "lng": -79.775,
        "dominant_species": [
            "Prosopis pallida (Algarrobo)",
            "Vachellia macracantha (Espino / Huaranjo)",
            "Capparis scabrida (Zapote)",
            "Bursera graveolens (Palo Santo)",
            "Loxopterygium huasango (Huasango)",
        ],
        "climate_type": "Árido cálido / Seco tropical (BWh/BSh)",
        "fluxnet_site_id": "PE-Pom / PE-BosqueSeco",
        "fluxnet_site_name": "Pómac Dry Forest Carbon Station",
        "mean_annual_precip_mm": 240.0,
        "mean_temp_c": 23.8,
        "elevation_m": 80.0,
        "baseline_agb": 38.2,
        "baseline_soc": 44.5,
        "description": "Ecosistema relicto único de algarrobals densos del norte peruano con alta adaptación al estrés hídrico extremo y recarga por eventos El Niño (ENSO).",
    },
    {
        "id": "montseny-biosphere",
        "name": "Reserva de la Biosfera del Montseny",
        "country": "España (Cataluña)",
        "biome": "Bosque Mediterráneo Montano / Templado Húmedo",
        "area_ha": 30120.0,
        "lat": 41.775,
        "lng": 2.441,
        "dominant_species": ["Quercus ilex (Encina)", "Fagus sylvatica (Haya)", "Castanea sativa (Castaño)", "Pinus sylvestris"],
        "climate_type": "Mediterráneo húmedo de montaña (Csb/Cfb)",
        "fluxnet_site_id": "ES-LJu / ES-Montseny",
        "fluxnet_site_name": "Montseny Quercus-Fagus Ecosite",
        "mean_annual_precip_mm": 865.0,
        "mean_temp_c": 11.8,
        "elevation_m": 1120.0,
        "baseline_agb": 92.4,
        "baseline_soc": 84.1,
        "description": "Ecotono bioclimático de transición submediterránea-eurosiberiana con alto gradiente altitudinal y vulnerabilidad a sequías estivales intensas.",
    },
    {
        "id": "guadarrama-pines",
        "name": "Parque Nacional Sierra de Guadarrama",
        "country": "España (Madrid / Castilla y León)",
        "biome": "Bosque de Coníferas de Alta Montaña",
        "area_ha": 33960.0,
        "lat": 40.783,
        "lng": -3.983,
        "dominant_species": ["Pinus sylvestris var. iberica (Pino albar)", "Pinus nigra", "Quercus pyrenaica (Rebollo)"],
        "climate_type": "Mediterráneo continentalizado de montaña (Dsb)",
        "fluxnet_site_id": "ES-Agu / ES-Gua",
        "fluxnet_site_name": "Guadarrama Scots Pine Tower",
        "mean_annual_precip_mm": 1150.0,
        "mean_temp_c": 9.4,
        "elevation_m": 1650.0,
        "baseline_agb": 118.6,
        "baseline_soc": 96.2,
        "description": "Masa continua de pinar de alta montaña con riesgo de incendios de copa en estiaje y estrés térmico por olas de calor estivales.",
    },
    {
        "id": "tapajos-flona",
        "name": "FLONA Tapajós - Amazonía Central",
        "country": "Brasil (Pará)",
        "biome": "Bosque Húmedo Tropical Siempreverde",
        "area_ha": 54900.0,
        "lat": -2.856,
        "lng": -54.958,
        "dominant_species": ["Manilkara huberi", "Bertholletia excelsa", "Carapa guianensis", "Couratari guianensis"],
        "climate_type": "Tropical monzónico (Am)",
        "fluxnet_site_id": "BR-Sa1 / BR-Sa3",
        "fluxnet_site_name": "KM67 Tapajós Primary Forest",
        "mean_annual_precip_mm": 2150.0,
        "mean_temp_c": 25.8,
        "elevation_m": 130.0,
        "baseline_agb": 245.8,
        "baseline_soc": 135.2,
        "description": "Ecosistema de dosel hiperdiverso (>45m) con intensa dinámica de recambio de biomasa, alta respiración nocturna y régimen de perturbaciones por El Niño.",
    },
    {
        "id": "landes-maritime",
        "name": "Macizo Forestal de las Landas de Gascuña",
        "country": "Francia (Nouvelle-Aquitaine)",
        "biome": "Pinar Atlántico de Llanura",
        "area_ha": 78500.0,
        "lat": 44.423,
        "lng": -0.732,
        "dominant_species": ["Pinus pinaster (Pino marítimo)", "Quercus robur", "Ulex europaeus"],
        "climate_type": "Oceánico templado (Cfb)",
        "fluxnet_site_id": "FR-Hes / FR-Bil",
        "fluxnet_site_name": "Bilos Maritime Pine Tower",
        "mean_annual_precip_mm": 940.0,
        "mean_temp_c": 13.2,
        "elevation_m": 65.0,
        "baseline_agb": 84.5,
        "baseline_soc": 62.8,
        "description": "Mayor masa boscosa continua cultivada de Europa occidental, altamente susceptible a tormentas severas e incendios de interfaz.",
    },
]

FLUX_TIMESERIES_DATA = [
    { "month": 'Ene 23', "timestamp": '2023-01', "temp_c": 5.2, "precip_mm": 45.0, "vpd_kpa": 0.42, "rad_mj_m2": 8.5, "pg3_gpp": 2.8, "pg3_nee": -0.6, "pg3_reco": 2.2, "pg3_agb": 92.4, "hybrid_gpp": 3.1, "hybrid_nee": -0.8, "hybrid_reco": 2.3, "hybrid_ci_lower": -1.1, "hybrid_ci_upper": -0.5, "fluxnet_gpp": 3.2, "fluxnet_nee": -0.9, "fluxnet_reco": 2.3 },
    { "month": 'Feb 23', "timestamp": '2023-02', "temp_c": 6.8, "precip_mm": 38.0, "vpd_kpa": 0.48, "rad_mj_m2": 11.2, "pg3_gpp": 3.9, "pg3_nee": -1.2, "pg3_reco": 2.7, "pg3_agb": 92.6, "hybrid_gpp": 4.2, "hybrid_nee": -1.4, "hybrid_reco": 2.8, "hybrid_ci_lower": -1.7, "hybrid_ci_upper": -1.1, "fluxnet_gpp": 4.4, "fluxnet_nee": -1.5, "fluxnet_reco": 2.9 },
    { "month": 'Mar 23', "timestamp": '2023-03', "temp_c": 10.4, "precip_mm": 72.0, "vpd_kpa": 0.65, "rad_mj_m2": 15.8, "pg3_gpp": 6.5, "pg3_nee": -2.8, "pg3_reco": 3.7, "pg3_agb": 93.1, "hybrid_gpp": 7.1, "hybrid_nee": -3.2, "hybrid_reco": 3.9, "hybrid_ci_lower": -3.6, "hybrid_ci_upper": -2.8, "fluxnet_gpp": 7.3, "fluxnet_nee": -3.3, "fluxnet_reco": 4.0 },
    { "month": 'Abr 23', "timestamp": '2023-04', "temp_c": 13.8, "precip_mm": 85.0, "vpd_kpa": 0.82, "rad_mj_m2": 19.4, "pg3_gpp": 9.4, "pg3_nee": -4.6, "pg3_reco": 4.8, "pg3_agb": 93.8, "hybrid_gpp": 10.2, "hybrid_nee": -5.1, "hybrid_reco": 5.1, "hybrid_ci_lower": -5.6, "hybrid_ci_upper": -4.6, "fluxnet_gpp": 10.5, "fluxnet_nee": -5.3, "fluxnet_reco": 5.2 },
    { "month": 'May 23', "timestamp": '2023-05', "temp_c": 17.5, "precip_mm": 92.0, "vpd_kpa": 1.15, "rad_mj_m2": 23.2, "pg3_gpp": 12.8, "pg3_nee": -6.4, "pg3_reco": 6.4, "pg3_agb": 94.7, "hybrid_gpp": 13.5, "hybrid_nee": -6.8, "hybrid_reco": 6.7, "hybrid_ci_lower": -7.3, "hybrid_ci_upper": -6.3, "fluxnet_gpp": 13.8, "fluxnet_nee": -7.0, "fluxnet_reco": 6.8 },
    { "month": 'Jun 23', "timestamp": '2023-06', "temp_c": 22.1, "precip_mm": 28.0, "vpd_kpa": 1.85, "rad_mj_m2": 26.5, "pg3_gpp": 11.2, "pg3_nee": -4.1, "pg3_reco": 7.1, "pg3_agb": 95.3, "hybrid_gpp": 10.8, "hybrid_nee": -3.5, "hybrid_reco": 7.3, "hybrid_ci_lower": -4.0, "hybrid_ci_upper": -3.0, "fluxnet_gpp": 10.6, "fluxnet_nee": -3.3, "fluxnet_reco": 7.3 },
    { "month": 'Jul 23', "timestamp": '2023-07', "temp_c": 26.4, "precip_mm": 12.0, "vpd_kpa": 2.65, "rad_mj_m2": 27.8, "pg3_gpp": 7.4, "pg3_nee": -0.6, "pg3_reco": 6.8, "pg3_agb": 95.5, "hybrid_gpp": 6.8, "hybrid_nee": 0.2, "hybrid_reco": 7.0, "hybrid_ci_lower": -0.3, "hybrid_ci_upper": 0.7, "fluxnet_gpp": 6.5, "fluxnet_nee": 0.4, "fluxnet_reco": 6.9 },
    { "month": 'Ago 23', "timestamp": '2023-08', "temp_c": 25.9, "precip_mm": 18.0, "vpd_kpa": 2.45, "rad_mj_m2": 24.1, "pg3_gpp": 6.8, "pg3_nee": -0.2, "pg3_reco": 6.6, "pg3_agb": 95.6, "hybrid_gpp": 6.2, "hybrid_nee": 0.6, "hybrid_reco": 6.8, "hybrid_ci_lower": 0.1, "hybrid_ci_upper": 1.1, "fluxnet_gpp": 6.0, "fluxnet_nee": 0.8, "fluxnet_reco": 6.8 },
    { "month": 'Sep 23', "timestamp": '2023-09', "temp_c": 20.8, "precip_mm": 68.0, "vpd_kpa": 1.45, "rad_mj_m2": 18.6, "pg3_gpp": 9.8, "pg3_nee": -4.2, "pg3_reco": 5.6, "pg3_agb": 96.2, "hybrid_gpp": 10.4, "hybrid_nee": -4.6, "hybrid_reco": 5.8, "hybrid_ci_lower": -5.1, "hybrid_ci_upper": -4.1, "fluxnet_gpp": 10.7, "fluxnet_nee": -4.8, "fluxnet_reco": 5.9 },
    { "month": 'Oct 23', "timestamp": '2023-10', "temp_c": 15.6, "precip_mm": 88.0, "vpd_kpa": 0.95, "rad_mj_m2": 13.4, "pg3_gpp": 7.2, "pg3_nee": -3.1, "pg3_reco": 4.1, "pg3_agb": 96.6, "hybrid_gpp": 7.8, "hybrid_nee": -3.5, "hybrid_reco": 4.3, "hybrid_ci_lower": -3.9, "hybrid_ci_upper": -3.1, "fluxnet_gpp": 8.0, "fluxnet_nee": -3.6, "fluxnet_reco": 4.4 },
    { "month": 'Nov 23', "timestamp": '2023-11', "temp_c": 9.8, "precip_mm": 95.0, "vpd_kpa": 0.58, "rad_mj_m2": 9.2, "pg3_gpp": 4.2, "pg3_nee": -1.4, "pg3_reco": 2.8, "pg3_agb": 96.8, "hybrid_gpp": 4.6, "hybrid_nee": -1.6, "hybrid_reco": 3.0, "hybrid_ci_lower": -1.9, "hybrid_ci_upper": -1.3, "fluxnet_gpp": 4.7, "fluxnet_nee": -1.7, "fluxnet_reco": 3.0 },
    { "month": 'Dic 23', "timestamp": '2023-12', "temp_c": 6.1, "precip_mm": 52.0, "vpd_kpa": 0.44, "rad_mj_m2": 7.4, "pg3_gpp": 2.9, "pg3_nee": -0.7, "pg3_reco": 2.2, "pg3_agb": 97.0, "hybrid_gpp": 3.2, "hybrid_nee": -0.9, "hybrid_reco": 2.3, "hybrid_ci_lower": -1.2, "hybrid_ci_upper": -0.6, "fluxnet_gpp": 3.3, "fluxnet_nee": -1.0, "fluxnet_reco": 2.3 },
]

SCENARIOS_DATA = [
    {
        "id": "scen-thinning",
        "name": "Clareo Selectivo Adaptativo",
        "tag": "Manejo Silvícola Activo",
        "type": "thinning",
        "description": "Reducción de densidad de un 25-30% de área basal en los años 5 y 25. Maximiza crecimiento individual de fustes dominantes, reduce competencia hídrica y atenúa la continuidad vertical del combustible.",
        "thinning_intensity_pct": 28.0,
        "thinning_schedule_years": [5, 25],
        "prescribed_burn_interval_years": 0,
        "reforestation_species": "Regeneración natural asistida",
        "fuel_break_width_m": 0.0,
        "metrics_summary": {
            "totalCarbon50Yr": 238.4,
            "carbonSequestrationRate": 3.12,
            "cumulativeHarvestedCarbon": 48.5,
            "meanFireRiskProb": 0.28,
            "fireResilienceScore": 84,
            "biodiversityShannonH": 2.75,
            "waterYieldM3Ha": 3420,
            "economicNPV_EUR_ha": 4250,
            "uncertaintyReductionPct": 34.2,
        },
        "trajectory": [
            { "year": 0, "agb": 92.4, "soc": 84.1, "deadwoodC": 12.0, "totalCarbon": 188.5, "lai": 3.8, "fireRiskProbability": 0.48, "canopyHeightM": 18.4, "stemDensityHa": 1100, "waterYieldMm": 310, "biodiversityIndex": 2.1 },
            { "year": 5, "agb": 74.2, "soc": 85.6, "deadwoodC": 18.4, "totalCarbon": 178.2, "lai": 2.7, "fireRiskProbability": 0.22, "canopyHeightM": 19.8, "stemDensityHa": 790, "waterYieldMm": 420, "biodiversityIndex": 2.4 },
            { "year": 10, "agb": 98.6, "soc": 89.2, "deadwoodC": 15.2, "totalCarbon": 203.0, "lai": 3.4, "fireRiskProbability": 0.26, "canopyHeightM": 22.1, "stemDensityHa": 760, "waterYieldMm": 375, "biodiversityIndex": 2.6 },
            { "year": 20, "agb": 142.1, "soc": 96.8, "deadwoodC": 14.0, "totalCarbon": 252.9, "lai": 4.1, "fireRiskProbability": 0.38, "canopyHeightM": 25.8, "stemDensityHa": 710, "waterYieldMm": 340, "biodiversityIndex": 2.7 },
            { "year": 25, "agb": 118.5, "soc": 98.4, "deadwoodC": 21.5, "totalCarbon": 238.4, "lai": 3.1, "fireRiskProbability": 0.21, "canopyHeightM": 26.9, "stemDensityHa": 520, "waterYieldMm": 435, "biodiversityIndex": 2.8 },
            { "year": 35, "agb": 158.4, "soc": 104.2, "deadwoodC": 16.8, "totalCarbon": 279.4, "lai": 3.9, "fireRiskProbability": 0.27, "canopyHeightM": 29.4, "stemDensityHa": 505, "waterYieldMm": 380, "biodiversityIndex": 2.8 },
            { "year": 50, "agb": 194.2, "soc": 112.5, "deadwoodC": 18.2, "totalCarbon": 324.9, "lai": 4.2, "fireRiskProbability": 0.31, "canopyHeightM": 32.6, "stemDensityHa": 480, "waterYieldMm": 360, "biodiversityIndex": 2.9 },
        ],
    },
    {
        "id": "scen-burns",
        "name": "Quemas Prescritas & Manejo de Combustible",
        "tag": "Mitigación de Incendios Extremos",
        "type": "prescribed_burn",
        "description": "Régimen de fuegos prescritos de baja intensidad cada 8 años en mosaico espacial. Consume restos finos superficiales manteniendo el dosel arbóreo intacto y reduciendo la probabilidad de incendios catastróficos.",
        "thinning_intensity_pct": 10.0,
        "thinning_schedule_years": [10],
        "prescribed_burn_interval_years": 8,
        "reforestation_species": "Especies piro-resistentes",
        "fuel_break_width_m": 30.0,
        "metrics_summary": {
            "totalCarbon50Yr": 212.8,
            "carbonSequestrationRate": 2.65,
            "cumulativeHarvestedCarbon": 12.0,
            "meanFireRiskProb": 0.16,
            "fireResilienceScore": 95,
            "biodiversityShannonH": 2.45,
            "waterYieldM3Ha": 3890,
            "economicNPV_EUR_ha": 2100,
            "uncertaintyReductionPct": 36.8,
        },
        "trajectory": [
            { "year": 0, "agb": 92.4, "soc": 84.1, "deadwoodC": 12.0, "totalCarbon": 188.5, "lai": 3.8, "fireRiskProbability": 0.48, "canopyHeightM": 18.4, "stemDensityHa": 1100, "waterYieldMm": 310, "biodiversityIndex": 2.1 },
            { "year": 5, "agb": 106.2, "soc": 83.2, "deadwoodC": 5.4, "totalCarbon": 194.8, "lai": 3.6, "fireRiskProbability": 0.14, "canopyHeightM": 19.5, "stemDensityHa": 1040, "waterYieldMm": 345, "biodiversityIndex": 2.3 },
            { "year": 10, "agb": 118.4, "soc": 85.0, "deadwoodC": 6.8, "totalCarbon": 210.2, "lai": 3.9, "fireRiskProbability": 0.16, "canopyHeightM": 21.2, "stemDensityHa": 980, "waterYieldMm": 360, "biodiversityIndex": 2.4 },
            { "year": 20, "agb": 139.6, "soc": 87.4, "deadwoodC": 6.1, "totalCarbon": 233.1, "lai": 4.0, "fireRiskProbability": 0.15, "canopyHeightM": 24.1, "stemDensityHa": 890, "waterYieldMm": 375, "biodiversityIndex": 2.5 },
            { "year": 35, "agb": 165.2, "soc": 91.8, "deadwoodC": 7.2, "totalCarbon": 264.2, "lai": 4.1, "fireRiskProbability": 0.18, "canopyHeightM": 27.5, "stemDensityHa": 790, "waterYieldMm": 380, "biodiversityIndex": 2.5 },
            { "year": 50, "agb": 188.0, "soc": 96.5, "deadwoodC": 8.1, "totalCarbon": 292.6, "lai": 4.2, "fireRiskProbability": 0.19, "canopyHeightM": 30.2, "stemDensityHa": 720, "waterYieldMm": 385, "biodiversityIndex": 2.6 },
        ],
    },
    {
        "id": "scen-restoration",
        "name": "Restauración Multifuncional & Enriquecimiento",
        "tag": "Secuestro & Biodiversidad Máxima",
        "type": "restoration",
        "description": "Plantación de enriquecimiento con especies autóctonas tardías en claros y zonas degradadas. Incrementa la complejidad estructural 3D, la retención de agua y la estabilidad del carbono orgánico.",
        "thinning_intensity_pct": 0.0,
        "thinning_schedule_years": [],
        "prescribed_burn_interval_years": 0,
        "reforestation_species": "Quercus petraea + Fagus sylvatica + Ilex aquifolium",
        "fuel_break_width_m": 15.0,
        "metrics_summary": {
            "totalCarbon50Yr": 285.6,
            "carbonSequestrationRate": 3.88,
            "cumulativeHarvestedCarbon": 0.0,
            "meanFireRiskProb": 0.32,
            "fireResilienceScore": 78,
            "biodiversityShannonH": 3.42,
            "waterYieldM3Ha": 2980,
            "economicNPV_EUR_ha": 3800,
            "uncertaintyReductionPct": 38.5,
        },
        "trajectory": [
            { "year": 0, "agb": 92.4, "soc": 84.1, "deadwoodC": 12.0, "totalCarbon": 188.5, "lai": 3.8, "fireRiskProbability": 0.48, "canopyHeightM": 18.4, "stemDensityHa": 1100, "waterYieldMm": 310, "biodiversityIndex": 2.1 },
            { "year": 5, "agb": 104.5, "soc": 86.8, "deadwoodC": 14.5, "totalCarbon": 205.8, "lai": 4.2, "fireRiskProbability": 0.44, "canopyHeightM": 19.8, "stemDensityHa": 1350, "waterYieldMm": 295, "biodiversityIndex": 2.6 },
            { "year": 10, "agb": 124.8, "soc": 92.4, "deadwoodC": 16.8, "totalCarbon": 234.0, "lai": 4.8, "fireRiskProbability": 0.38, "canopyHeightM": 21.6, "stemDensityHa": 1280, "waterYieldMm": 280, "biodiversityIndex": 2.9 },
            { "year": 20, "agb": 168.4, "soc": 105.6, "deadwoodC": 22.4, "totalCarbon": 296.4, "lai": 5.4, "fireRiskProbability": 0.34, "canopyHeightM": 25.4, "stemDensityHa": 1150, "waterYieldMm": 270, "biodiversityIndex": 3.2 },
            { "year": 35, "agb": 224.6, "soc": 121.2, "deadwoodC": 28.5, "totalCarbon": 374.3, "lai": 5.9, "fireRiskProbability": 0.30, "canopyHeightM": 29.8, "stemDensityHa": 980, "waterYieldMm": 260, "biodiversityIndex": 3.4 },
            { "year": 50, "agb": 272.5, "soc": 138.4, "deadwoodC": 34.2, "totalCarbon": 445.1, "lai": 6.2, "fireRiskProbability": 0.28, "canopyHeightM": 33.5, "stemDensityHa": 860, "waterYieldMm": 255, "biodiversityIndex": 3.6 },
        ],
    },
    {
        "id": "scen-laissez-faire",
        "name": "Laissez-Faire / No Intervención (Línea Base)",
        "tag": "Evolución Espontánea + Cambio Climático",
        "type": "laissez_faire",
        "description": "Ausencia total de gestión selvícola bajo escenario climático RCP 8.5. Alta acumulación inicial de combustible que culmina en un gran incendio forestal en el año 18.",
        "thinning_intensity_pct": 0.0,
        "thinning_schedule_years": [],
        "prescribed_burn_interval_years": 0,
        "reforestation_species": "Ninguna (sucesión no asistida)",
        "fuel_break_width_m": 0.0,
        "metrics_summary": {
            "totalCarbon50Yr": 142.2,
            "carbonSequestrationRate": 0.95,
            "cumulativeHarvestedCarbon": 0.0,
            "meanFireRiskProb": 0.68,
            "fireResilienceScore": 32,
            "biodiversityShannonH": 1.85,
            "waterYieldM3Ha": 2650,
            "economicNPV_EUR_ha": -850,
            "uncertaintyReductionPct": 22.0,
        },
        "trajectory": [
            { "year": 0, "agb": 92.4, "soc": 84.1, "deadwoodC": 12.0, "totalCarbon": 188.5, "lai": 3.8, "fireRiskProbability": 0.48, "canopyHeightM": 18.4, "stemDensityHa": 1100, "waterYieldMm": 310, "biodiversityIndex": 2.1 },
            { "year": 5, "agb": 108.2, "soc": 86.4, "deadwoodC": 16.8, "totalCarbon": 211.4, "lai": 4.4, "fireRiskProbability": 0.58, "canopyHeightM": 19.9, "stemDensityHa": 1040, "waterYieldMm": 285, "biodiversityIndex": 2.2 },
            { "year": 10, "agb": 128.5, "soc": 89.2, "deadwoodC": 24.5, "totalCarbon": 242.2, "lai": 4.9, "fireRiskProbability": 0.72, "canopyHeightM": 21.8, "stemDensityHa": 980, "waterYieldMm": 260, "biodiversityIndex": 2.1 },
            { "year": 18, "agb": 38.4, "soc": 68.5, "deadwoodC": 45.2, "totalCarbon": 152.1, "lai": 1.2, "fireRiskProbability": 0.88, "canopyHeightM": 8.5, "stemDensityHa": 220, "waterYieldMm": 520, "biodiversityIndex": 1.2 },
            { "year": 25, "agb": 48.6, "soc": 69.8, "deadwoodC": 32.0, "totalCarbon": 150.4, "lai": 2.1, "fireRiskProbability": 0.35, "canopyHeightM": 11.2, "stemDensityHa": 680, "waterYieldMm": 440, "biodiversityIndex": 1.6 },
            { "year": 35, "agb": 72.4, "soc": 73.5, "deadwoodC": 22.4, "totalCarbon": 168.3, "lai": 3.0, "fireRiskProbability": 0.48, "canopyHeightM": 14.8, "stemDensityHa": 950, "waterYieldMm": 360, "biodiversityIndex": 1.9 },
            { "year": 50, "agb": 104.2, "soc": 79.4, "deadwoodC": 18.5, "totalCarbon": 202.1, "lai": 3.7, "fireRiskProbability": 0.62, "canopyHeightM": 18.2, "stemDensityHa": 1080, "waterYieldMm": 315, "biodiversityIndex": 2.0 },
        ],
    },
]

def generate_spatial_stands(region: Region, grid_size: int = 16):
    """
    Generates spatial forest stands with realistic topographic and biophysical variation.
    Using a 16x16 grid (256 stands per region) for initial database population.
    """
    stands = []
    for y in range(grid_size):
        for x in range(grid_size):
            nx = x / grid_size
            ny = y / grid_size
            elev = region.elevation_m + math.sin(nx * math.pi) * 450.0 + math.cos(ny * math.pi * 1.5) * 280.0
            slope = max(2.0, abs(math.sin(nx * 4.0) * 35.0 + math.cos(ny * 3.0) * 18.0))
            aspect = "Solana (Sur)" if nx > 0.5 else "Umbría (Norte)"
            aspect_factor = 0.85 if nx > 0.5 else 1.2
            elev_factor = 1.0 - max(0.0, (elev - region.elevation_m) / 1200.0)
            noise = math.sin(x * 12.3 + y * 7.7) * 0.15

            base_agb = region.baseline_agb * aspect_factor * elev_factor * (1.0 + noise)
            agb = max(12.0, min(380.0, base_agb))
            height = max(4.0, min(46.0, math.sqrt(agb) * 2.8 + noise * 3.0))
            ndvi = max(0.25, min(0.92, 0.55 + (agb / 300.0) * 0.35 + noise * 0.05))
            ndwi = max(-0.1, min(0.65, (ndvi - 0.45) * 0.7))
            fuel_moisture = max(15.0, min(95.0, 75.0 * (1.0 - (0.25 if nx > 0.5 else 0.0)) - (12.0 if slope > 25.0 else 0.0)))
            fwi_risk = max(0.04, min(0.96, (100.0 - fuel_moisture) * 0.009 + (slope / 45.0) * 0.2 + (0.15 if agb > 80.0 else 0.0)))
            soc = max(35.0, region.baseline_soc * elev_factor * (1.0 + noise * 0.5))
            gpp = max(1.2, (ndvi * 16.5) * (1.0 - fwi_risk * 0.3))
            reco = max(0.8, gpp * 0.58 + (-0.5 if elev > 1400.0 else 0.4))
            nee = reco - gpp

            species_list = region.dominant_species or ["Bosque Mixto"]
            species = species_list[int((nx * 2.5 + ny * 1.5)) % len(species_list)]
            stand_age = int(round(25 + (agb / max(1.0, region.baseline_agb)) * 35))

            lat = region.lat + (ny - 0.5) * 0.15
            lng = region.lng + (nx - 0.5) * 0.18
            stand_id = f"STAND-{region.id[:3].upper()}-{str(y).zfill(2)}{str(x).zfill(2)}"

            stand = Stand(
                stand_id=stand_id,
                region_id=region.id,
                x=x,
                y=y,
                lat=round(lat, 5),
                lng=round(lng, 5),
                species=species,
                stand_age=stand_age,
                agb_mgc_ha=round(agb, 1),
                gedi_height_m=round(height, 1),
                ndvi=round(ndvi, 3),
                ndwi=round(ndwi, 3),
                fuel_moisture_pct=round(fuel_moisture, 1),
                fwi_risk=round(fwi_risk, 3),
                soc_mgc_ha=round(soc, 1),
                gpp_flux=round(gpp, 2),
                nee_flux=round(nee, 2),
                reco_flux=round(reco, 2),
                slope_pct=round(slope, 1),
                aspect=aspect,
                elevation_m=int(round(elev)),
            )
            stands.append(stand)
    return stands

def seed():
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check existing regions
        existing_regions = db.query(Region).count()
        if existing_regions == 0:
            logger.info("Seeding Regions and Spatial Stands...")
            for r_data in REGIONS_DATA:
                region = Region(**r_data)
                db.add(region)
                db.flush()

                # Generate stands for this region
                stands = generate_spatial_stands(region, grid_size=16)
                db.add_all(stands)
                logger.info(f" -> Region '{region.name}' added with {len(stands)} spatial stands.")

            # Seed Flux TimeSeries (associated with first region)
            first_region_id = REGIONS_DATA[0]["id"]
            for f_data in FLUX_TIMESERIES_DATA:
                fts = FluxTimeSeries(region_id=first_region_id, **f_data)
                db.add(fts)
            logger.info(f" -> Added {len(FLUX_TIMESERIES_DATA)} flux time series points.")

            # Seed Scenarios
            for s_data in SCENARIOS_DATA:
                sc = Scenario(**s_data)
                db.add(sc)
            logger.info(f" -> Added {len(SCENARIOS_DATA)} management scenarios.")

            db.commit()
            logger.info("✅ Database seeded successfully!")
        else:
            logger.info(f"Database already contains {existing_regions} regions. Skipping seed.")
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error during seed: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed()
