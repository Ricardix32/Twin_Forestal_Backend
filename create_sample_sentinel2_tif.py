"""
Script para generar un GeoTIFF multiespectral de muestra Sentinel-2 (6 bandas)
referenciado espacialmente sobre Tambopata, Madre de Dios, Perú (EPSG:4326).
"""
import os
import numpy as np
import rasterio
from rasterio.transform import from_origin

def create_sample_sentinel2():
    output_dir = os.path.join(os.path.dirname(__file__), "data", "sentinel2")
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, "S2A_MSIL2A_20230815T145731_N0509_R125_T19LDF_sample.tif")

    if os.path.exists(filepath):
        print(f"Sample Sentinel-2 GeoTIFF already exists at: {filepath}")
        return filepath

    print(f"Creating sample Sentinel-2 GeoTIFF: {filepath}")

    # Dimensions: 128x128 pixels covering Tambopata region
    width = 128
    height = 128
    bands_count = 6  # B02 (Blue), B03 (Green), B04 (Red), B08 (NIR), B11 (SWIR1), B12 (SWIR2)

    # Upper-left coordinates near Puerto Maldonado / Tambopata
    west = -69.35
    north = -12.75
    pixel_size = 0.001  # approx 100m in lat/lon degrees
    transform = from_origin(west, north, pixel_size, pixel_size)

    # Generate synthetic multispectral surface reflectances (scaled 0 - 10000)
    # NIR (B08) high for dense Amazon rainforest (~4000-6000)
    # Red (B04) low (~300-800) -> High NDVI
    b02 = np.random.randint(200, 500, (height, width), dtype=np.uint16)
    b03 = np.random.randint(300, 700, (height, width), dtype=np.uint16)
    b04 = np.random.randint(250, 650, (height, width), dtype=np.uint16)
    b08 = np.random.randint(4200, 6800, (height, width), dtype=np.uint16)
    b11 = np.random.randint(1200, 2200, (height, width), dtype=np.uint16)
    b12 = np.random.randint(500, 1100, (height, width), dtype=np.uint16)

    stack = np.stack([b02, b03, b04, b08, b11, b12])

    with rasterio.open(
        filepath,
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=bands_count,
        dtype=np.uint16,
        crs="EPSG:4326",
        transform=transform,
    ) as dst:
        dst.write(stack)
        dst.set_band_description(1, "B02 - Blue (490nm)")
        dst.set_band_description(2, "B03 - Green (560nm)")
        dst.set_band_description(3, "B04 - Red (665nm)")
        dst.set_band_description(4, "B08 - NIR (842nm)")
        dst.set_band_description(5, "B11 - SWIR1 (1610nm)")
        dst.set_band_description(6, "B12 - SWIR2 (2190nm)")

    print(f"[OK] Generated sample Sentinel-2 GeoTIFF with 6 bands (128x128 pixels).")
    return filepath

if __name__ == "__main__":
    create_sample_sentinel2()
