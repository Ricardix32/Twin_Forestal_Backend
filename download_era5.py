"""
Script para descargar series meteorológicas y bioclimáticas reales de ECMWF ERA5-Land Reanalysis
para las regiones de estudio de SilvaTwin (Temperatura 2m, Precipitación, VPD, Radiación Solar).
"""
import os
import sys
import json
import logging
import urllib.request
import pandas as pd
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("era5_downloader")

DATA_DIR = Path(__file__).resolve().parent / "data" / "era5"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Coordenadas geográficas de las regiones SilvaTwin
REGIONS = {
    "madre-de-dios-peru": {
        "name": "Reserva Nacional Tambopata (Madre de Dios)",
        "lat": -12.825,
        "lon": -69.288,
        "timezone": "America/Lima",
    },
    "bosque-seco-norperuano": {
        "name": "Bosque de Pómac (Lambayeque)",
        "lat": -6.475,
        "lon": -79.775,
        "timezone": "America/Lima",
    },
    "montseny-biosphere": {
        "name": "Reserva del Montseny (España)",
        "lat": 41.775,
        "lon": 2.441,
        "timezone": "Europe/Madrid",
    },
}

def fetch_era5_land_reanalysis(region_id: str = "madre-de-dios-peru", year: int = 2023):
    region_info = REGIONS.get(region_id, REGIONS["madre-de-dios-peru"])
    lat = region_info["lat"]
    lon = region_info["lon"]
    tz = region_info["timezone"]
    region_name = region_info["name"]

    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"

    url = (
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}"
        f"&daily=temperature_2m_mean,temperature_2m_max,temperature_2m_min,"
        f"precipitation_sum,vapour_pressure_deficit_max,shortwave_radiation_sum"
        f"&timezone={urllib.parse.quote(tz)}"
    )

    logger.info(f"Descargando reanálisis ECMWF ERA5-Land para '{region_name}' ({year})...")
    logger.info(f"Coordenadas: Lat {lat}, Lon {lon} | Intervalo: {start_date} a {end_date}")

    req = urllib.request.Request(url, headers={"User-Agent": "SilvaTwin-ERA5-Ingest/1.0"})
    with urllib.request.urlopen(req, timeout=30) as res:
        payload = json.loads(res.read().decode("utf-8"))

    daily_data = payload.get("daily", {})
    if not daily_data or "time" not in daily_data:
        raise ValueError("Respuesta vacía o formato inválido de ERA5-Land.")

    df = pd.DataFrame({
        "date": daily_data["time"],
        "temp_mean_c": daily_data["temperature_2m_mean"],
        "temp_max_c": daily_data["temperature_2m_max"],
        "temp_min_c": daily_data["temperature_2m_min"],
        "precip_mm": daily_data["precipitation_sum"],
        "vpd_max_kpa": daily_data["vapour_pressure_deficit_max"],
        "rad_solar_mj_m2": daily_data["shortwave_radiation_sum"],
    })

    # Guardar serie diaria
    daily_filename = f"era5_land_daily_{year}_{region_id}.csv"
    daily_path = DATA_DIR / daily_filename
    df.to_csv(daily_path, index=False)
    logger.info(f"✅ Guardado archivo diario: {daily_path} ({len(df)} días registrados)")

    # Calcular promedios mensuales para calibración del modelo 3-PG y series de flujos
    df["month"] = pd.to_datetime(df["date"]).dt.to_period("M")
    monthly_df = df.groupby("month").agg({
        "temp_mean_c": "mean",
        "precip_mm": "sum",
        "vpd_max_kpa": "mean",
        "rad_solar_mj_m2": "mean",
    }).reset_index()

    monthly_df["month_label"] = monthly_df["month"].dt.strftime("%b %y")
    monthly_df["temp_mean_c"] = monthly_df["temp_mean_c"].round(1)
    monthly_df["precip_mm"] = monthly_df["precip_mm"].round(1)
    monthly_df["vpd_max_kpa"] = monthly_df["vpd_max_kpa"].round(2)
    monthly_df["rad_solar_mj_m2"] = monthly_df["rad_solar_mj_m2"].round(1)

    monthly_filename = f"era5_land_monthly_{year}_{region_id}.csv"
    monthly_path = DATA_DIR / monthly_filename
    monthly_df.to_csv(monthly_path, index=False)
    logger.info(f"✅ Guardado resumen mensual: {monthly_path} (12 meses)")
    logger.info(f"   Precipitación anual acumulada: {monthly_df['precip_mm'].sum():.1f} mm | Temp media: {monthly_df['temp_mean_c'].mean():.1f} °C")

    return str(daily_path), str(monthly_path)

if __name__ == "__main__":
    reg = sys.argv[1] if len(sys.argv) > 1 else "madre-de-dios-peru"
    fetch_era5_land_reanalysis(reg, 2023)
