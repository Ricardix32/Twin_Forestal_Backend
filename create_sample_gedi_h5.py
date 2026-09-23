"""
Script para generar un archivo de muestra NASA GEDI HDF5 (.h5)
con la estructura oficial para pruebas inmediatas del pipeline.
"""
import os
import h5py
import numpy as np

def create_sample_gedi():
    output_dir = os.path.join(os.path.dirname(__file__), "data", "gedi")
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, "GEDI02_A_2023245120000_O19842_01_T05342_02_003_01_V002_sample.h5")

    if os.path.exists(filepath):
        print(f"Sample file already exists at: {filepath}")
        return filepath

    print(f"Creating sample GEDI HDF5 file: {filepath}")
    with h5py.File(filepath, "w") as f:
        # Create metadata attributes
        f.attrs["instrument"] = "GEDI"
        f.attrs["granule_type"] = "GEDI02_A"

        # Create two simulated laser beams
        beams = ["BEAM0000", "BEAM0001"]
        num_shots = 300

        # Centered near Tambopata, Peru [-12.825, -69.288]
        base_lat = -12.825
        base_lon = -69.288

        for beam in beams:
            grp = f.create_group(beam)
            lats = base_lat + np.random.uniform(-0.06, 0.06, num_shots)
            lons = base_lon + np.random.uniform(-0.06, 0.06, num_shots)
            quality = np.random.choice([1, 1, 1, 0], num_shots)  # 75% valid quality

            # Generate 101 height return percentiles (RH0 to RH100)
            rh_matrix = np.zeros((num_shots, 101), dtype=np.float32)
            # RH98 canopy top height between 18m and 45m
            top_heights = np.random.uniform(18.0, 44.5, num_shots)
            for i in range(num_shots):
                rh_matrix[i] = np.sort(np.random.uniform(0.0, top_heights[i], 101))
                rh_matrix[i, 98] = top_heights[i]

            grp.create_dataset("lat_lowestmode", data=lats, dtype=np.float64)
            grp.create_dataset("lon_lowestmode", data=lons, dtype=np.float64)
            grp.create_dataset("quality_flag", data=quality, dtype=np.int32)
            grp.create_dataset("rh", data=rh_matrix, dtype=np.float32)

    print(f"[OK] Generated sample GEDI HDF5 file with {len(beams)} beams and {num_shots} shots each.")
    return filepath

if __name__ == "__main__":
    create_sample_gedi()
