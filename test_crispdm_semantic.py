"""
Script de verificación para el servicio CRISP-DM y la inferencia semántica con LangChain.
"""

import sys
from pathlib import Path

# Configurar encoding seguro para terminales Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Añadir raíz del backend al path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.core.database import SessionLocal
from app.services.crispdm_service import CrispDmService
from app.services.semantic_twin import (
    StandTelemetryInput,
    run_semantic_evaluation,
    get_langflow_flow_schema,
)

def test_crispdm_overview():
    print("-> Probando CrispDmService.get_full_overview()...")
    db = SessionLocal()
    try:
        overview = CrispDmService.get_full_overview(db, "madre-de-dios-peru")
        assert "phases" in overview, "Faltan fases en el overview"
        assert len(overview["phases"]) == 6, f"Se esperaban 6 fases, se obtuvieron {len(overview['phases'])}"
        print(f"[OK] Overview obtenido correctamente con {len(overview['phases'])} fases.")
        for p in overview["phases"]:
            print(f"   [Fase {p['phaseNumber']}] {p['name']} ({p['crispEquivalent']}) -> {p['status']}")
    finally:
        db.close()

def test_crispdm_phase_actions():
    print("\n-> Probando acciones por fase...")
    db = SessionLocal()
    try:
        for phase_num in range(1, 7):
            phase_id = f"fase-{phase_num}"
            res = CrispDmService.run_phase_action(phase_id, {"regionId": "madre-de-dios-peru"}, db)
            assert "status" in res, f"Acción de fase {phase_id} no retornó status"
            print(f"[OK] Fase {phase_num} ejecutada con éxito: {res.get('phase', phase_id)} -> {res.get('status')}")
    finally:
        db.close()

def test_semantic_twin_inference():
    print("\n-> Probando inferencia semántica LangChain (Dao et al., 2025)...")
    telemetry = StandTelemetryInput(
        stand_id="STAND-TEST-TAM-01",
        region_name="Reserva Nacional Tambopata",
        species="Bertholletia excelsa",
        agb_mgc_ha=260.0,
        gedi_height_m=35.0,
        fuel_moisture_pct=18.5,
        fwi_risk=0.78,
        ndvi=0.84,
        slope_pct=22.0,
        days_without_rain=28,
    )
    decision = run_semantic_evaluation(telemetry)
    print(f"[OK] Decisión generada para {decision.stand_id}:")
    print(f"   Nivel de riesgo: {decision.risk_level}")
    print(f"   Comportamiento: {decision.fire_behavior}")
    print(f"   Intervención:   {decision.adaptive_intervention}")
    print(f"   Impacto C:      {decision.carbon_tradeoff_assessment}")
    print(f"   Fundamento:     {decision.scientific_basis}")

def test_langflow_schema():
    print("\n-> Probando esquema de flujo Langflow...")
    schema = get_langflow_flow_schema()
    assert "nodes" in schema and "edges" in schema, "Esquema inválido de Langflow"
    print(f"[OK] Esquema Langflow verificado: {len(schema['nodes'])} nodos y {len(schema['edges'])} aristas.")

if __name__ == "__main__":
    test_crispdm_overview()
    test_crispdm_phase_actions()
    test_semantic_twin_inference()
    test_langflow_schema()
    print("\n[EXITO] Todas las pruebas del módulo CRISP-DM y LangChain pasaron satisfactoriamente.")
