import sys, json
sys.path.insert(0, "dashboard")
import gps_manager

# Test 1: Coordonnees dans la zone cacaoyere (Soubre)
print("=== Test 1: Soubre (6.3, -6.5) ===")
r1 = gps_manager.verifier_deforestation(6.3, -6.5)
print(json.dumps(r1, ensure_ascii=False, indent=2))

# Test 2: Coordonnees hors zone
print("\n=== Test 2: Paris (48.8, 2.3) ===")
r2 = gps_manager.verifier_deforestation(48.8, 2.3)
print(json.dumps(r2, ensure_ascii=False, indent=2))
