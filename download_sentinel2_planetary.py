"""
Script para descargar e ingerir recortes multiespectrales reales de Copernicus Sentinel-2 L2A
directamente desde Microsoft Planetary Computer STAC API para SilvaTwin.
"""
import os
import sys
import logging
from pathlib import Path
import numpy as np
import rasterio
from rasterio.windows import from_bounds
from rasterio.warp import transform_bounds
import pystac_client
import planetary_computer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("sentinel2_downloader")

DATA_DIR = Path(__file__).resolve().parent / "data" / "sentinel2"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Bounding boxes for predefined SilvaTwin regions [min_lon, min_lat, max_lon, max_lat]
REGION_BBOXES = {
    "madre-de-dios-peru": {
        "name": "Reserva Nacional Tambopata",
        "bbox": [-69.35, -12.88, -69.23, -12.77],
        "date_range": "2023-08-01/2023-09-30",  # Dry season (low clouds)
    },
    "bosque-seco-norperuano": {
        "name": "Bosque de Pómac (Lambayeque)",
        "bbox": [-79.82, -6.52, -79.72, -6.42],
        "date_range": "2023-06-01/2023-09-30",
    },
    "montseny-biosphere": {
        "name": "Reserva del Montseny (España)",
        "bbox": [2.35, 41.72, 2.50, 41.83],
        "date_range": "2023-06-01/2023-08-31",
    },
}

def fetch_sentinel2_planetary(region_id: str = "madre-de-dios-peru", max_clouds: float = 10.0):
    region_info = REGION_BBOXES.get(region_id, REGION_BBOXES["madre-de-dios-peru"])
    bbox = region_info["bbox"]
    date_range = region_info["date_range"]
    region_name = region_info["name"]

    logger.info(f"Conectando a Microsoft Planetary Computer STAC API...")
    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
    )

    logger.info(f"Buscando escenas Sentinel-2 L2A sobre '{region_name}' (BBox: {bbox}, Nubes < {max_clouds}%)...")
    search = catalog.search(
        collections=["sentinel-2-l2a"],
        bbox=bbox,
        datetime=date_range,
        query={"eo:cloud_cover": {"lt": max_clouds}},
        max_items=5,
    )

    items = list(search.items())
    if not items:
        logger.warning("No se encontraron escenas con ese umbral. Intentando con nubes < 20%...")
        search = catalog.search(
            collections=["sentinel-2-l2a"],
            bbox=bbox,
            datetime=date_range,
            query={"eo:cloud_cover": {"lt": 20.0}},
            max_items=5,
        )
        items = list(search.items())

    if not items:
        raise RuntimeError(f"No se encontraron escenas Sentinel-2 disponibles para {region_name} en las fechas indicadas.")

    # Sort by lowest cloud cover
    items.sort(key=lambda it: it.properties.get("eo:cloud_cover", 100))
    selected_item = items[0]
    cloud_pct = selected_item.properties.get("eo:cloud_cover", 0)
    capture_date = selected_item.datetime.strftime("%Y-%m-%d")
    item_id = selected_item.id

    logger.info(f"✓ Escena seleccionada: {item_id}")
    logger.info(f"  Fecha de adquisición: {capture_date} | Nubosidad escena: {cloud_pct:.1f}%")

    # Output filename
    output_filename = f"S2_L2A_{region_id}_{capture_date}.tif"
    output_path = DATA_DIR / output_filename

    # Bands to extract (10m bands: B02, B03, B04, B08)
    band_keys = ["B02", "B03", "B04", "B08"]
    band_names = ["B02 (Blue)", "B03 (Green)", "B04 (Red)", "B08 (NIR)"]

    logger.info("Configurando lector de ventanas Cloud-Optimized GeoTIFF (COG)...")
    gdal_env = {
        "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
        "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": ".tif",
        "GDAL_HTTP_TIMEOUT": "20",
    }

    band_arrays = []
    out_profile = None

    with rasterio.Env(**gdal_env):
        for idx, b_key in enumerate(band_keys):
            asset_href = selected_item.assets[b_key].href
            logger.info(f" -> Leyendo ventana de {band_names[idx]} vía COG streaming...")

            with rasterio.open(asset_href) as src:
                # Transform bbox from WGS84 to native Sentinel-2 UTM CRS
                minx, miny, maxx, maxy = transform_bounds("EPSG:4326", src.crs, *bbox)
                window = from_bounds(minx, miny, maxx, maxy, src.transform)

                data = src.read(1, window=window)
                win_transform = src.window_transform(window)

                if idx == 0:
                    out_profile = src.profile.copy()
                    out_profile.update({
                        "driver": "GTiff",
                        "count": len(band_keys),
                        "dtype": data.dtype,
                        "height": data.shape[0],
                        "width": data.shape[1],
                        "transform": win_transform,
                        "compress": "deflate",
                    })

                band_arrays.append(data)

        # Write stacked GeoTIFF to data/sentinel2/
        logger.info(f"Escribiendo GeoTIFF multiespectral ({out_profile['width']}x{out_profile['height']} px, 4 bandas)...")
        with rasterio.open(output_path, "w", **out_profile) as dst:
            for b_idx, arr in enumerate(band_arrays, start=1):
                dst.write(arr, b_idx)
                dst.set_band_description(b_idx, band_names[b_idx - 1])

    size_mb = round(output_path.stat().st_size / (1024 * 1024), 2)
    logger.info(f"✅ Descarga completada exitosamente:")
    logger.info(f"   Archivo: {output_path}")
    logger.info(f"   Tamaño: {size_mb} MB (Recorte ligero y optimizado)")
    logger.info(f"   Bandas: B02, B03, B04, B08 (listo para cálculo de NDVI en Fase 3)")

    return {
        "status": "success",
        "regionId": region_id,
        "regionName": region_name,
        "file": str(output_path),
        "filename": output_filename,
        "sizeMB": size_mb,
        "captureDate": capture_date,
        "cloudCover": cloud_pct,
        "sceneId": item_id,
    }

if __name__ == "__main__":
    target_region = sys.argv[1] if len(sys.argv) > 1 else "madre-de-dios-peru"
    fetch_sentinel2_planetary(target_region)
