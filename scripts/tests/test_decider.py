import requests

BASE_URL = "http://localhost:5000"

def test(nom, donnees):
    print(f"\n--- {nom} ---")
    r = requests.post(f"{BASE_URL}/decider", json=donnees)
    res = r.json()
    print(f"Action       : {res['action']}")
    print(f"Conflit      : {res['conflit']}")
    print(f"Mode risque  : {res['maladie']['mode_risque']}")
    print(f"Irrigation   : {res['irrigation']['decision']}")
    print(f"Pulverisation: {res['pulverisation']['decision']}")
    if res['maladie']['message']:
        print(f"Message      : {res['maladie']['message']}")
    if res['message_conflit']:
        print(f"Conflit msg  : {res['message_conflit']}")

donnees_base = {
    "temperature"  : 29,
    "humidite_air" : 72,
    "humidite_sol" : 35,
    "vitesse_vent" : 5,
    "pluie"        : 0
}

# CAS 1 — Sans photo
test("CAS 1 — Sans photo", donnees_base)

# CAS 2 — BLACKPOD detecte
test("CAS 2 — BLACKPOD", {**donnees_base, "maladie_detectee": "BLACKPOD"})

# CAS 3 — FROSTYPOD detecte
test("CAS 3 — FROSTYPOD", {**donnees_base, "maladie_detectee": "FROSTYPOD"})

# CAS 4 — MIRID detecte
test("CAS 4 — MIRID", {**donnees_base, "maladie_detectee": "MIRID"})