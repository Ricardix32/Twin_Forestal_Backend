# Copernicus Sentinel-2 MSI Data Directory

Coloca aquí los recortes GeoTIFF multiespectrales de Sentinel-2 L2A:
* **Formatos soportados:** `.tif` / `.tiff` (Cloud-Optimized GeoTIFF o estándar GeoTIFF).
* **Bandas clave:**
  * B04 (Rojo - 665 nm) a 10m
  * B08 (Infrarrojo Cercano NIR - 842 nm) a 10m
  * B11 (Infrarrojo de Onda Corta SWIR - 1610 nm) a 20m
* El pipeline extraerá automáticamente las capas de NDVI y NDWI para la visualización del mapa 2D y la tabla `stands` en PostGIS.
