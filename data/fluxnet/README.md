# FLUXNET2015 Tower Data Directory

Coloca aquí los archivos CSV mensuales o semi-horarios descargados de FLUXNET2015:
* **Formato soportado:** `.csv`
* **Columnas esperadas (Tier 1):**
  * `TIMESTAMP`
  * `GPP_NT_VUT_REF` (Productividad Primaria Bruta)
  * `NEE_VUT_REF` (Intercambio Neto del Ecosistema)
  * `RECO_NT_VUT_REF` (Respiración del Ecosistema)
* Los datos se insertarán en la tabla `flux_timeseries` de PostGIS para validar los modelos 3-PG y Deep Learning.
