import sys
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.region import Region
from app.models.stand import Stand
from app.models.scenario import Scenario

def run_tests():
    print("=" * 60)
    print(" SILVATWIN BACKEND VERIFICATION SUITE")
    print("=" * 60)

    client = TestClient(app)

    # 1. Health Check
    print("\n1. Testing GET /health...")
    res = client.get("/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print(f" -> OK: {res.json()}")

    # 2. Database verification
    print("\n2. Verifying database records...")
    db = SessionLocal()
    try:
        reg_count = db.query(Region).count()
        stand_count = db.query(Stand).count()
        scen_count = db.query(Scenario).count()
        print(f" -> Regions in DB: {reg_count}")
        print(f" -> Stands in DB: {stand_count}")
        print(f" -> Scenarios in DB: {scen_count}")
        assert reg_count > 0, "No regions found in database. Did you run seed_data.py?"
    finally:
        db.close()

    # 3. GET /api/v1/regions
    print("\n3. Testing GET /api/v1/regions...")
    res = client.get("/api/v1/regions")
    assert res.status_code == 200, f"Get regions failed: {res.text}"
    regions = res.json()
    assert len(regions) > 0
    print(f" -> OK: Retrieved {len(regions)} regions (First: {regions[0]['name']})")
    print(f" -> Region center: {regions[0]['center']}")

    # 4. GET /api/v1/stands/region/{id}
    print(f"\n4. Testing GET /api/v1/stands/region/{regions[0]['id']}...")
    res = client.get(f"/api/v1/stands/region/{regions[0]['id']}?limit=10")
    assert res.status_code == 200, f"Get stands failed: {res.text}"
    stands = res.json()
    assert len(stands) > 0
    first_stand = stands[0]
    # Check for either camelCase (standId) or snake_case
    stand_id_val = first_stand.get("standId") or first_stand.get("stand_id")
    agb_val = first_stand.get("agbMgC_ha") or first_stand.get("agb_mgc_ha")
    print(f" -> OK: Retrieved {len(stands)} stands (First standId: {stand_id_val}, AGB: {agb_val} Mg C/ha)")

    # 5. POST /api/v1/simulations/3pg
    print("\n5. Testing POST /api/v1/simulations/3pg...")
    sim_payload = {
        "species": "pine",
        "years": 20,
        "thinning": 25.0,
        "prescribedBurn": True,
        "droughtSeverity": 1.2
    }
    res = client.post("/api/v1/simulations/3pg", json=sim_payload)
    assert res.status_code == 200, f"Simulation failed: {res.text}"
    sim_results = res.json()["results"]
    assert len(sim_results) == 21  # yr 0 to 20
    print(f" -> OK: 3-PG simulation generated {len(sim_results)} years of trajectory data")
    print(f" -> Year 0 Total Carbon: {sim_results[0]['totalCarbon']} Mg C/ha")
    print(f" -> Year 20 Total Carbon: {sim_results[-1]['totalCarbon']} Mg C/ha")

    # 6. POST /api/v1/ai-advisor (offline fallback test)
    print("\n6. Testing POST /api/v1/ai-advisor...")
    ai_payload = {
        "prompt": "¿Cómo optimizar la asimilación de datos con GEDI y Sentinel-2?",
        "context": {"region": regions[0]['name']}
    }
    res = client.post("/api/v1/ai-advisor", json=ai_payload)
    assert res.status_code == 200, f"AI advisor failed: {res.text}"
    advisor_resp = res.json()["response"]
    assert len(advisor_resp) > 50
    print(f" -> OK: AI Advisor response received ({len(advisor_resp)} chars)")

    # 7. GET /api/v1/scenarios
    print("\n7. Testing GET /api/v1/scenarios...")
    res = client.get("/api/v1/scenarios")
    assert res.status_code == 200
    scenarios = res.json()
    print(f" -> OK: Retrieved {len(scenarios)} management scenarios")

    # 8. GET /api/v1/pipeline/status
    print("\n8. Testing GET /api/v1/pipeline/status...")
    res = client.get("/api/v1/pipeline/status")
    assert res.status_code == 200, f"Pipeline status failed: {res.text}"
    status = res.json()
    print(f" -> OK: Pipeline scanned {len(status)} categories. GEDI files: {status['gedi']['filesCount']}")

    # 9. POST /api/v1/pipeline/run
    print("\n9. Testing POST /api/v1/pipeline/run...")
    res = client.post("/api/v1/pipeline/run", json={"regionId": regions[0]["id"]})
    assert res.status_code == 200, f"Pipeline run failed: {res.text}"
    run_res = res.json()
    print(f" -> OK: Pipeline executed for {run_res['regionId']}. Processed: {len(run_res['processedComponents'])} components.")

    # 10. POST /api/v1/models/predict-agb (Tarea 1.1)
    print("\n10. Testing POST /api/v1/models/predict-agb (Stacking Inferences)...")
    model_payload = {
        "rh98_m": 28.5,
        "ndvi": 0.82,
        "savi": 0.65,
        "ndwi": 0.35,
        "fmc_pct": 88.0,
        "vpd_kpa": 1.15
    }
    res = client.post("/api/v1/models/predict-agb", json=model_payload)
    assert res.status_code == 200, f"Model predict failed: {res.text}"
    pred_data = res.json()
    assert pred_data["agb_pred_mgc_ha"] > 0
    assert pred_data["ci_95_lower"] < pred_data["agb_pred_mgc_ha"] < pred_data["ci_95_upper"]
    print(f" -> OK: AGB predicted: {pred_data['agb_pred_mgc_ha']} Mg C/ha (95% CI: [{pred_data['ci_95_lower']}, {pred_data['ci_95_upper']}])")

    # 11. GET /api/v1/models/info
    print("\n11. Testing GET /api/v1/models/info...")
    res = client.get("/api/v1/models/info")
    assert res.status_code == 200, f"Model info failed: {res.text}"
    model_info = res.json()
    assert model_info["r2"] >= 0.85
    print(f" -> OK: Model '{model_info['model_name']}', R2: {model_info['r2']}, RMSE: {model_info['rmse']}")

    # 12. GET /api/v1/stands/geojson/{region_id} (Tarea 1.2)
    print(f"\n12. Testing GET /api/v1/stands/geojson/{regions[0]['id']}...")
    res = client.get(f"/api/v1/stands/geojson/{regions[0]['id']}")
    assert res.status_code == 200, f"Stands GeoJSON failed: {res.text}"
    geojson_data = res.json()
    assert geojson_data["type"] == "FeatureCollection"
    assert len(geojson_data["features"]) > 0
    first_feat = geojson_data["features"][0]
    assert "geometry" in first_feat and "properties" in first_feat
    assert "agb_mgc_ha" in first_feat["properties"]
    print(f" -> OK: GeoJSON FeatureCollection with {len(geojson_data['features'])} points verified")

    # 13. GET /api/v1/validation/scientific-metrics (Tarea 1.3)
    print("\n13. Testing GET /api/v1/validation/scientific-metrics (H1, H2, H3)...")
    res = client.get("/api/v1/validation/scientific-metrics")
    assert res.status_code == 200, f"Validation metrics failed: {res.text}"
    val_data = res.json()
    assert "main_hypothesis" in val_data or "mainHypothesis" in val_data
    main_h = val_data.get("main_hypothesis") or val_data.get("mainHypothesis")
    assert main_h["status"] == "CONFIRMADA"
    curves = val_data.get("distribution_curves") or val_data.get("distributionCurves")
    assert len(curves) > 20
    print(f" -> OK: Main hypothesis status: {main_h['status']} (Achieved reduction: {main_h['achieved_reduction_pct']}%)")
    print(f" -> OK: Monte Carlo probability density curves generated: {len(curves)} sample coordinates")

    # 14. POST /api/v1/scenarios/simulate-custom (Tarea 1.4)
    print("\n14. Testing POST /api/v1/scenarios/simulate-custom...")
    custom_scen_payload = {
        "region_id": regions[0]["id"],
        "name": "Simulación Silvícola Adaptativa Test",
        "thinning_intensity_pct": 20.0,
        "thinning_schedule_years": [15, 30],
        "prescribed_burn_frequency_years": 5,
        "fuel_break_width_m": 30.0,
        "horizon_years": 50,
        "climate_scenario": "rcp45"
    }
    res = client.post("/api/v1/scenarios/simulate-custom", json=custom_scen_payload)
    assert res.status_code == 200, f"Custom scenario simulation failed: {res.text}"
    sim_data = res.json()
    metrics = sim_data.get("metrics_summary") or sim_data.get("metricsSummary")
    traj = sim_data.get("trajectory")
    assert len(traj) > 5
    print(f" -> OK: Custom scenario '{sim_data['name']}' simulated across {len(traj)} intervals")
    print(f" -> OK: 50-year Total Carbon: {metrics['totalCarbon50Yr']} Mg C/ha, Resilience Score: {metrics['fireResilienceScore']}")

    print("\n" + "=" * 60)
    print(" ALL 14 VERIFICATION CHECKS PASSED SUCCESSFULLY! ")
    print("=" * 60)


if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print(f"\n[ERROR] VERIFICATION FAILED: {repr(e)}")
        sys.exit(1)
