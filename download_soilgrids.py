"""
Script para descargar GeoTIFFs reales de ISRIC SoilGrids 2.0 (Carbono Orgánico del Suelo 0-30 cm)
vía OGC Web Coverage Service (WCS) en proyección EPSG:4326 para SilvaTwin.
"""
import os
import sys
import logging
import urllib.request
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("soilgrids_downloader")

DATA_DIR = Path(__file__).resolve().parent / "data" / "soilgrids"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Bounding boxes [min_lon, min_lat, max_lon, max_lat] para las regiones de SilvaTwin
REGION_BBOXES = {
    "madre-de-dios-peru": {
        "name": "Reserva Nacional Tambopata (Madre de Dios)",
        "bbox": [-69.35, -12.88, -69.23, -12.77],
    },
    "bosque-seco-norperuano": {
        "name": "Bosque de Pómac (Lambayeque)",
        "bbox": [-79.82, -6.52, -79.72, -6.42],
    },
    "montseny-biosphere": {
        "name": "Reserva del Montseny (España)",
        "bbox": [2.35, 41.72, 2.50, 41.83],
    },
}

def download_soilgrids_coverage(
    region_id: str = "madre-de-dios-peru",
    property_name: str = "ocs",
    depth: str = "0-30cm",
    statistic: str = "mean",
):
    """
    Descarga el GeoTIFF recortado de ISRIC SoilGrids usando el servicio WCS 2.0.1.
    Propiedades comunes:
      - ocs: Soil organic carbon stock (t/ha o decitones/ha)
      - soc: Soil organic carbon content (dg/kg)
      - clay: Clay content (g/kg)
      - sand: Sand content (g/kg)
      - bdod: Bulk density (cg/cm³)
    """
    region_info = REGION_BBOXES.get(region_id, REGION_BBOXES["madre-de-dios-peru"])
    bbox = region_info["bbox"]
    region_name = region_info["name"]
    min_lon, min_lat, max_lon, max_lat = bbox

    coverage_id = f"{property_name}_{depth}_{statistic}"
    wcs_url = (
        f"https://maps.isric.org/mapserv?map=/map/{property_name}.map"
        f"&SERVICE=WCS&VERSION=2.0.1&REQUEST=GetCoverage"
        f"&COVERAGEID={coverage_id}"
        f"&SUBSETTINGCRS=http://www.opengis.net/def/crs/EPSG/0/4326"
        f"&SUBSET=Long({min_lon},{max_lon})"
        f"&SUBSET=Lat({min_lat},{max_lat})"
        f"&OUTPUTCRS=http://www.opengis.net/def/crs/EPSG/0/4326"
        f"&FORMAT=image/tiff"
    )

    filename = f"soilgrids_{property_name}_{depth}_{region_id}.tif"
    output_path = DATA_DIR / filename

    logger.info(f"Conectando a ISRIC SoilGrids WCS para '{region_name}'...")
    logger.info(f"Capa: {coverage_id} | Coordenadas: [{min_lon}, {min_lat}, {max_lon}, {max_lat}]")

    req = urllib.request.Request(
        wcs_url,
        headers={"User-Agent": "SilvaTwin-Scientific-Digitalis/1.0"},
    )

    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            data = response.read()

        if len(data) < 1000 or data.startswith(b"<?xml") or b"ExceptionReport" in data:
            logger.error(f"Error devuelto por el servidor WCS:\n{data.decode('utf-8', errors='ignore')}")
            return None

        with open(output_path, "wb") as f:
            f.write(data)

        size_kb = round(len(data) / 1024, 2)
        logger.info(f"✅ Descarga exitosa: {output_path} ({size_kb} KB)")

        # Validar con rasterio si está disponible
        try:
            import rasterio
            with rasterio.open(output_path) as src:
                logger.info(f"   Dimensiones: {src.width}x{src.height} píxeles | CRS: {src.crs} | Bandas: {src.count}")
                arr = src.read(1)
                valid = arr[arr > 0]
                if len(valid) > 0:
                    # En SoilGrids ocs, el factor de escala es 10 (decitoneladas a t/ha)
                    mean_val = round(float(valid.mean() / 10.0), 2)
                    logger.info(f"   Stock medio de Carbono Orgánico (SOC): {mean_val} t/ha (Mg C/ha)")
        except Exception as e:
            logger.warning(f"No se pudo validar rasterio: {e}")

        return str(output_path)
    except Exception as e:
        logger.error(f"Fallo al descargar de SoilGrids: {e}")
        return None

if __name__ == "__main__":
    reg = sys.argv[1] if len(sys.argv) > 1 else "madre-de-dios-peru"
    download_soilgrids_coverage(reg)
