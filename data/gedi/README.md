# NASA GEDI LiDAR Data Directory

Coloca aquí tus archivos GEDI descargados de NASA Earthdata:
* **Formatos soportados:** `.h5` (HDF5 oficial GEDI L2A / L4A) o `.parquet` / `.csv`.
* **Productos principales:**
  * `GEDI02_A`: Perfiles verticales de retorno de energía y percentiles `rh` (RH25, RH50, RH75, RH98).
  * `GEDI04_A`: Densidad de biomasa aérea estimada (`agbDensity` en Mg C/ha).
* El motor del backend (`pipeline_service.py`) leerá automáticamente este directorio mediante `h5py` y filtrará los disparos de alta calidad (`quality_flag == 1`).
