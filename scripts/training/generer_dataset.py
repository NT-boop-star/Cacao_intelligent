import pandas as pd
import numpy as np
import os

np.random.seed(42)
NB_JOURS = 2000


def get_saison(mois):
    """
    Retourne le code saison selon le mois
    pour la zone cacaoière du sud de CI.

    Source : WeatherSpark Abidjan + SODEXAM

    0 = Grande saison seche   (Novembre à Mars)
        -> saison très chaude, 29-32°C, harmattan
    1 = Grande saison pluies  (Avril à Juillet)
        -> pluies intenses, 28-31°C
    2 = Petite saison seche   (Août à Septembre)
        -> saison fraîche, 27-28°C
    3 = Petite saison pluies  (Octobre)
        -> retour pluies, 29-31°C
    """
    if mois in [11, 12, 1, 2, 3]:
        return 0   # grande saison seche
    elif mois in [4, 5, 6, 7]:
        return 1   # grande saison pluies
    elif mois in [8, 9]:
        return 2   # petite saison seche
    else:
        return 3   # petite saison pluies (Octobre)


def probabilite_pluie(mois):
    """
    Probabilité de pluie par mois basée sur les vraies données
    pluviométriques de la zone cacaoière de CI.
    Source : données climatiques Abidjan/Soubré + SODEXAM
    Pluviométrie annuelle : 1500-2000mm (FAO / UNESCO)
    """
    proba_par_mois = {
        1  : 0.10,  # Janvier   ->  18mm  | Grande saison seche
        2  : 0.15,  # Fevrier   ->  32mm  | Grande saison seche
        3  : 0.35,  # Mars      ->  91mm  | Grande saison seche
        4  : 0.45,  # Avril     -> 115mm  | Grande saison pluies
        5  : 0.60,  # Mai       -> 203mm  | Grande saison pluies
        6  : 0.75,  # Juin      -> 342mm  | Pic absolu
        7  : 0.55,  # Juillet   -> 122mm  | Grande saison pluies
        8  : 0.15,  # Aout      ->  23mm  | Petite saison seche
        9  : 0.20,  # Septembre ->  56mm  | Petite saison seche
        10 : 0.50,  # Octobre   -> 149mm  | Petite saison pluies
        11 : 0.45,  # Novembre  -> 131mm  | Grande saison seche
        12 : 0.20,  # Decembre  ->  91mm  | Grande saison seche
    }
    return proba_par_mois[mois]


def generer_dataset():
    """
    Génère un dataset simulé basé sur les paramètres
    agronomiques réels du cacaoyer en Côte d'Ivoire.

    Sources scientifiques :
    - WeatherSpark Abidjan    : températures réelles par mois
                                saison très chaude Nov-Mai (31°C+)
                                saison fraîche Juil-Sep (< 28°C)
    - Wikipedia CI + SODEXAM : 4 saisons zone sud CI
    - FAO / UNESCO            : paramètres agronomiques cacaoyer
    - Universalis             : température optimale cacaoyer
    - Wikifarmer              : sensibilité au stress hydrique
    - Etude HAL 2022          : variabilité climatique CI

    Saisons corrigées v5 (source WeatherSpark) :
    - Grande saison seche   : Novembre à Mars
    - Grande saison pluies  : Avril à Juillet
    - Petite saison seche   : Août à Septembre
    - Petite saison pluies  : Octobre

    Logique d'irrigation :
    - DECLENCHEMENT : humidite_sol < 45% suffit seul (FAO)
    - AGGRAVATION   : temperature > 28 ET humidite_air < 70
    - BLOCAGE       : pluie >= 2mm OU pluie_prevue = 1
    """

    print("Generation du dataset v5 en cours...")
    print("Sources : WeatherSpark, SODEXAM, FAO, UNESCO, Universalis")

    # -- MOIS ET SAISON -------------------------------------------
    mois_par_jour = np.clip(
        np.array([(j % 365) // 30 + 1 for j in range(NB_JOURS)]),
        1, 12
    )
    saison_par_jour = np.array([get_saison(m) for m in mois_par_jour])

    # -- TEMPERATURE ----------------------------------------------
    # Températures réelles par saison — source WeatherSpark Abidjan
    #
    # Grande saison seche  (Nov-Mars) : max 29-32°C, min 24-25°C
    # Grande saison pluies (Avr-Juil) : max 28-31°C, min 23-25°C
    # Petite saison seche  (Aout-Sep) : max 27-28°C, min 23°C
    # Petite saison pluies (Oct)      : max 29-31°C, min 24°C
    temperature = np.array([
        np.random.uniform(29, 32) if s == 0 else  # grande saison seche
        np.random.uniform(28, 31) if s == 1 else  # grande saison pluies
        np.random.uniform(27, 28) if s == 2 else  # petite saison seche
        np.random.uniform(29, 31)                 # petite saison pluies
        for s in saison_par_jour
    ])

    # -- HUMIDITE AIR ---------------------------------------------
    # Varie selon la saison — source : Wikipedia CI
    # Grande saison seche  : 40-65% (harmattan dessèche l'air)
    # Grande saison pluies : 75-100% (air très humide)
    # Petite saison seche  : 55-75%
    # Petite saison pluies : 70-95%
    humidite_air = np.array([
        np.random.uniform(40, 65)  if s == 0 else
        np.random.uniform(75, 100) if s == 1 else
        np.random.uniform(55, 75)  if s == 2 else
        np.random.uniform(70, 95)
        for s in saison_par_jour
    ])

    # -- HUMIDITE SOL ---------------------------------------------
    # Seuil critique : < 45% -> stress hydrique (FAO)
    # Grande saison seche  : sol très sec (20-50%)
    # Grande saison pluies : sol bien humide (50-95%)
    # Petite saison seche  : sol moyen (30-65%)
    # Petite saison pluies : sol humide (45-85%)
    humidite_sol = np.array([
        np.random.uniform(20, 50) if s == 0 else
        np.random.uniform(50, 95) if s == 1 else
        np.random.uniform(30, 65) if s == 2 else
        np.random.uniform(45, 85)
        for s in saison_par_jour
    ])

    # -- VITESSE VENT ---------------------------------------------
    # Harmattan en grande saison seche -> vent plus fort
    # Source : Routard CI
    vitesse_vent = np.array([
        np.random.uniform(5, 30) if s == 0 else
        np.random.uniform(0, 15)
        for s in saison_par_jour
    ])

    # -- PLUIE ----------------------------------------------------
    pluie = np.array([
        np.random.uniform(1, 35)
        if np.random.random() < probabilite_pluie(mois_par_jour[j])
        else 0
        for j in range(NB_JOURS)
    ])

    # -- PLUIE PREVUE ---------------------------------------------
    pluie_prevue = np.array([
        1 if np.random.random() < probabilite_pluie(mois_par_jour[j])
        else 0
        for j in range(NB_JOURS)
    ])

    # -- LOGIQUE D'IRRIGATION -------------------------------------

    # CONDITION 1 — Sol trop sec (condition suffisante)
    # Seuil : 45% (FAO — tension hydrique 20 kPa)
    sol_trop_sec = (humidite_sol < 45)

    # CONDITION 2 — Stress thermique (renforce le besoin)
    # Chaleur + air sec accélèrent l'évapotranspiration
    # Source : Universalis + UNESCO
    stress_thermique = (
        (temperature  > 28) &
        (humidite_air < 70)
    )

    # CONDITION 3 — Blocage par la pluie
    pluie_presente = (
        (pluie        >= 2) |
        (pluie_prevue == 1)
    )

    # DECISION FINALE
    besoin_irrigation = (
        (sol_trop_sec | stress_thermique) & ~pluie_presente
    ).astype(int)

    # -- CONSTRUCTION DU TABLEAU ----------------------------------
    dataset = pd.DataFrame({
        "mois"         : mois_par_jour,
        "saison"       : saison_par_jour,
        "temperature"  : np.round(temperature, 1),
        "humidite_air" : np.round(humidite_air, 1),
        "humidite_sol" : np.round(humidite_sol, 1),
        "vitesse_vent" : np.round(vitesse_vent, 1),
        "pluie"        : np.round(pluie, 1),
        "pluie_prevue" : pluie_prevue,
        "irrigation"   : besoin_irrigation
    })

    # -- SAUVEGARDE -----------------------------------------------
    os.makedirs("data", exist_ok=True)
    dataset.to_csv("data/dataset.csv", index=False)

    print(f"\nDataset genere      : {NB_JOURS} lignes")
    print(f"Fichier             : data/dataset.csv")
    print(f"\nApercu des 5 premieres lignes :")
    print(dataset.head())
    print(f"\nStatistiques :")
    print(f"   Irrigation necessaire : {besoin_irrigation.sum()} "
          f"({besoin_irrigation.mean()*100:.1f}%)")
    print(f"   Pas d'irrigation      : {NB_JOURS - besoin_irrigation.sum()} "
          f"({(1-besoin_irrigation.mean())*100:.1f}%)")
    print(f"   Jours de pluie        : {(pluie > 0).sum()}")
    print(f"\nRepartition des causes :")
    print(f"   Sol trop sec seul     : "
          f"{(sol_trop_sec & ~stress_thermique & ~pluie_presente).sum()}")
    print(f"   Stress thermique seul : "
          f"{(stress_thermique & ~sol_trop_sec & ~pluie_presente).sum()}")
    print(f"   Les deux combines     : "
          f"{(sol_trop_sec & stress_thermique & ~pluie_presente).sum()}")
    print(f"   Bloques par la pluie  : "
          f"{(pluie_presente & (sol_trop_sec | stress_thermique)).sum()}")
    print(f"\nIrrigation par saison :")
    for code, nom in [(0, "Grande saison seche  (Nov-Mars)"),
                      (1, "Grande saison pluies (Avr-Juil)"),
                      (2, "Petite saison seche  (Aout-Sep)"),
                      (3, "Petite saison pluies (Oct)     ")]:
        mask  = saison_par_jour == code
        total = mask.sum()
        irrig = besoin_irrigation[mask].sum()
        print(f"   {nom} : {irrig}/{total} "
              f"({irrig/total*100:.1f}%)")


if __name__ == "__main__":
    generer_dataset()