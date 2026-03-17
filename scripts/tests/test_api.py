import requests

BASE_URL = "http://localhost:5000"

# Coordonnées des principales zones cacaoières CI
ZONES = {
    "Soubre"    : {"lat": 5.7833,  "lon": -6.5833},
    "San Pedro" : {"lat": 4.7485,  "lon": -6.6363},
    "Man"       : {"lat": 7.4126,  "lon": -7.5538},
    "Abidjan"   : {"lat": 5.3600,  "lon": -4.0083},
}


def test_statut():
    print("Test route / ...")
    reponse  = requests.get(f"{BASE_URL}/")
    resultat = reponse.json()
    print(f"   Statut      : {resultat['statut']}")
    print(f"   Irrigation  : {resultat['modeles']['irrigation']}")
    print(f"   Pesticide   : {resultat['modeles']['pesticide']}")
    print(f"   Mois        : {resultat['contexte_actuel']['mois']}")
    print(f"   Saison      : {resultat['contexte_actuel']['saison']}")
    print(f"   Zone        : {resultat['contexte_actuel']['zone_defaut']['ville']}")


def test_meteo(zone="Soubre"):
    print(f"\nTest route /meteo — zone : {zone} ...")
    lat = ZONES[zone]["lat"]
    lon = ZONES[zone]["lon"]
    reponse  = requests.get(f"{BASE_URL}/meteo?lat={lat}&lon={lon}")
    resultat = reponse.json()

    if resultat["statut"] == "ok":
        m = resultat["meteo"]
        print(f"   Ville          : {m['ville']}")
        print(f"   Temperature    : {m['temperature']} C")
        print(f"   Humidite air   : {m['humidite_air']} %")
        print(f"   Vent           : {m['vitesse_vent']} km/h")
        print(f"   Pluie          : {m['pluie']} mm")
        print(f"   Pluie 24h      : {m['pluie_prevue_24h']}")
        print(f"   Pluie 3h       : {m['pluie_prevue_3h']}")
        print(f"   Saison         : {m['saison']}")
    else:
        print(f"   Erreur : {resultat['message']}")


def test_predire(zone="Soubre"):
    print(f"\nTest route /predire — zone : {zone} ...")

    donnees = {
        "latitude"     : ZONES[zone]["lat"],
        "longitude"    : ZONES[zone]["lon"],
        "temperature"  : 31.5,
        "humidite_air" : 68.0,
        "humidite_sol" : 28.0,
        "vitesse_vent" : 5.2,
        "pluie"        : 0.0
    }

    reponse  = requests.post(f"{BASE_URL}/predire", json=donnees)
    resultat = reponse.json()

    print(f"   Decision       : {resultat['decision']}")
    print(f"   Message        : {resultat['message']}")
    print(f"   Confiance      : {resultat['confiance']}%")
    print(f"   Saison         : {resultat['contexte']['saison']}")
    print(f"   Pluie prevue   : {resultat['contexte']['pluie_prevue']}")
    print(f"   Localisation   : {resultat['contexte']['latitude']}, "
          f"{resultat['contexte']['longitude']}")


def test_sans_gps():
    print(f"\nTest route /predire — sans GPS (defaut Soubre) ...")

    donnees = {
        "temperature"  : 31.5,
        "humidite_air" : 68.0,
        "humidite_sol" : 28.0,
        "vitesse_vent" : 5.2,
        "pluie"        : 0.0
    }

    reponse  = requests.post(f"{BASE_URL}/predire", json=donnees)
    resultat = reponse.json()

    print(f"   Decision       : {resultat['decision']}")
    print(f"   Message        : {resultat['message']}")
    print(f"   Localisation   : {resultat['contexte']['latitude']}, "
          f"{resultat['contexte']['longitude']} (defaut)")


def test_pulveriser(zone="Soubre"):
    print(f"\nTest route /pulveriser — zone : {zone} ...")

    donnees = {
        "latitude"     : ZONES[zone]["lat"],
        "longitude"    : ZONES[zone]["lon"],
        "temperature"  : 27.5,
        "humidite_air" : 72.0,
        "vitesse_vent" : 5.0,
        "pluie"        : 0.0
    }

    reponse  = requests.post(f"{BASE_URL}/pulveriser", json=donnees)
    resultat = reponse.json()

    print(f"   Decision           : {resultat['decision']}")
    print(f"   Message            : {resultat['message']}")
    print(f"   Confiance          : {resultat['confiance']}%")
    print(f"   Risque pourriture  : {resultat['risques']['pourriture_brune']}")
    print(f"   Risque mirides     : {resultat['risques']['mirides']}")
    print(f"   Saison             : {resultat['contexte']['saison']}")
    print(f"   Pluie prevue 3h    : {resultat['contexte']['pluie_prevue_3h']}")


def test_decider_conflit():
    print(f"\nTest route /decider — simulation conflit ...")

    # Sol sec (28%) + conditions pulverisation OK en aout
    # -> les deux modeles veulent agir -> conflit attendu
    donnees = {
        "latitude"     : 5.7833,
        "longitude"    : -6.5833,
        "temperature"  : 27.5,
        "humidite_air" : 72.0,
        "humidite_sol" : 28.0,
        "vitesse_vent" : 5.0,
        "pluie"        : 0.0
    }

    reponse  = requests.post(f"{BASE_URL}/decider", json=donnees)
    resultat = reponse.json()

    print(f"   Action finale      : {resultat['action']}")
    print(f"   Conflit detecte    : {resultat['conflit']}")
    print(f"   Irrigation         : {resultat['irrigation']['decision']} "
          f"({resultat['irrigation']['confiance']}%)")
    print(f"   Pulverisation      : {resultat['pulverisation']['decision']} "
          f"({resultat['pulverisation']['confiance']}%)")
    print(f"   Saison             : {resultat['contexte']['saison']}")
    print(f"   Risque pourriture  : "
          f"{resultat['pulverisation']['risques']['pourriture_brune']}")
    print(f"   Risque mirides     : "
          f"{resultat['pulverisation']['risques']['mirides']}")
    if resultat['message_conflit']:
        print(f"   Message conflit    : {resultat['message_conflit']}")


def test_decider_no_conflit():
    print(f"\nTest route /decider — sans conflit (sol humide) ...")

    # Sol humide (75%) -> pas d'irrigation
    # Conditions favorables pulverisation -> pulveriser seulement
    donnees = {
        "latitude"     : 5.7833,
        "longitude"    : -6.5833,
        "temperature"  : 27.5,
        "humidite_air" : 72.0,
        "humidite_sol" : 75.0,   # sol humide -> pas d'irrigation
        "vitesse_vent" : 5.0,
        "pluie"        : 0.0
    }

    reponse  = requests.post(f"{BASE_URL}/decider", json=donnees)
    resultat = reponse.json()

    print(f"   Action finale      : {resultat['action']}")
    print(f"   Conflit detecte    : {resultat['conflit']}")
    print(f"   Irrigation         : {resultat['irrigation']['decision']}")
    print(f"   Pulverisation      : {resultat['pulverisation']['decision']}")
    if resultat['message_conflit']:
        print(f"   Message conflit    : {resultat['message_conflit']}")


if __name__ == "__main__":
    print("=" * 50)
    print("   TEST API CACAO INTELLIGENT v4")
    print("=" * 50)

    test_statut()
    test_meteo("Soubre")
    test_predire("Soubre")
    test_sans_gps()
    test_pulveriser("Soubre")
    test_decider_conflit()
    test_decider_no_conflit()

    print("\n" + "=" * 50)
    print("   Tests termines")
    print("=" * 50)