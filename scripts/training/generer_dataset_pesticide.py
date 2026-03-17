import pandas as pd
import numpy as np
import os

np.random.seed(42)
NB_JOURS = 2000


def get_saison(mois):
    """
    4 saisons zone cacaoière sud CI.
    Source : WeatherSpark Abidjan + SODEXAM

    0 = Grande saison seche   (Novembre a Mars)
        -> tres chaud 29-32 C, harmattan, humidite 40-65%
    1 = Grande saison pluies  (Avril a Juillet)
        -> chaud 28-31 C, pluies intenses, humidite 75-100%
    2 = Petite saison seche   (Aout a Septembre)
        -> frais 27-28 C, humidite 55-75%  <- MEILLEURE PERIODE
    3 = Petite saison pluies  (Octobre)
        -> chaud 29-31 C, humidite 70-95%
    """
    if mois in [11, 12, 1, 2, 3]:
        return 0
    elif mois in [4, 5, 6, 7]:
        return 1
    elif mois in [8, 9]:
        return 2
    else:
        return 3


def probabilite_pluie(mois):
    """
    Probabilites pluviometriques reelles zone cacaoiere CI.
    Source : SODEXAM + donnees climatiques Abidjan/Soubre
    """
    proba = {
        1 : 0.10,   # Janvier   ->  18mm  | Grande saison seche
        2 : 0.15,   # Fevrier   ->  32mm  | Grande saison seche
        3 : 0.35,   # Mars      ->  91mm  | Grande saison seche
        4 : 0.45,   # Avril     -> 115mm  | Grande saison pluies
        5 : 0.60,   # Mai       -> 203mm  | Grande saison pluies
        6 : 0.75,   # Juin      -> 342mm  | Grande saison pluies (pic)
        7 : 0.55,   # Juillet   -> 122mm  | Grande saison pluies
        8 : 0.15,   # Aout      ->  23mm  | Petite saison seche
        9 : 0.20,   # Septembre ->  56mm  | Petite saison seche
        10: 0.50,   # Octobre   -> 149mm  | Petite saison pluies
        11: 0.45,   # Novembre  -> 131mm  | Grande saison seche
        12: 0.20,   # Decembre  ->  91mm  | Grande saison seche
    }
    return proba[mois]


def generer_dataset():
    """
    Genere un dataset pour le modele de decision
    de pulverisation de pesticides sur cacaoyer en CI.

    DECISION : pulveriser = 1 ou ne pas pulveriser = 0

    ================================================================
    REGLES AGRONOMIQUES DETAILLEES

    A) CONDITIONS METEOROLOGIQUES FAVORABLES
    ----------------------------------------
    Toutes ces conditions doivent etre reunies simultanement :

    1. TEMPERATURE < 30 C
       - Au-dessus de 28 C + humidite < 70% : effet phytotoxique
         Source : Syngenta Agro
       - En zone tropicale CI on adapte le seuil a 30 C max
         (temperatures rarement sous 25 C selon WeatherSpark)
       - Consequence : grande saison seche (29-32 C) est difficile

    2. HUMIDITE AIR entre 60% et 95%
       - < 60% : les gouttes s'evaporent avant absorption
         Source : Agrifind / BASF Agro
       - > 80% : optimal, cuticules dilatees -> meilleure absorption
         Source : Agrifind
       - > 95% : produit ruisselle comme apres pluie
         Source : Weenat / Sencrop

    3. VITESSE VENT < 12 km/h
       - > 12 km/h : derive significative du produit
       - > 19 km/h : interdit reglementairement (arrete 2006)
         Source : ARVALIS / BASF Agro
       - Consequence : harmattan (grande saison seche) bloque souvent

    4. PLUIE = 0 mm
       - Pluie presente dilue et emporte le produit
         Source : ARVALIS

    5. PLUIE PREVUE 3H = 0
       - Fenetre de 3h minimum apres traitement exigee
         Source : ARVALIS / Sencrop

    B) RISQUE MALADIE PRESENT
    -------------------------
    Au moins un risque doit etre actif :

    1. RISQUE POURRITURE BRUNE (Phytophthora palmivora)
       - Champignon favorise par humidite elevee et pluies
       - Actif pendant : Grande saison pluies (Avr-Juil)
                         Petite saison pluies (Oct)
       - Condition : humidite_air > 75% sur plusieurs jours
         Source : Cahiers Agricultures 2024 / Yara CI

    2. RISQUE MIRIDES (insectes capsides)
       - Insectes suceurs actifs en saison seche et chaleur
       - Actif pendant : Grande saison seche (Nov-Mars)
                         Petite saison seche (Aout-Sep)
       - Condition : temperature > 27 C ET saison seche
         Source : Diallo 2023 / IRD / Organic Africa
       - Les mirides representent 20% des pertes mondiales annuelles

    C) PERIODES REELLES DE TRAITEMENT EN CI
    ----------------------------------------
    D'apres les praticiens cacaoyers CI :
    - Avril a Juin      : risque pourriture brune monte
    - Juillet a Sept    : transition + petite saison seche (optimal)
    - Octobre a Janvier : risque mixte pourriture + mirides
    Source : Cooperatives cacaoieres CI / Conseil Cafe-Cacao

    D) CONCLUSION - DECISION FINALE
    --------------------------------
    PULVERISER si :
    (conditions_meteo_favorables) ET (risque_maladie_actif)
    ================================================================
    """

    print("Generation du dataset pesticide v2 en cours...")
    print("Sources : WeatherSpark, ARVALIS, Agrifind, Cahiers Agri 2024,")
    print("          Diallo 2023, IRD, Syngenta, BASF, Conseil Cafe-Cacao CI")

    # -- MOIS ET SAISON -------------------------------------------
    mois_par_jour = np.clip(
        np.array([(j % 365) // 30 + 1 for j in range(NB_JOURS)]),
        1, 12
    )
    saison_par_jour = np.array([get_saison(m) for m in mois_par_jour])

    # -- TEMPERATURE ----------------------------------------------
    # Temperatures reelles par saison — source WeatherSpark Abidjan
    #
    # Grande saison seche  (Nov-Mar) : 29-32 C -> souvent > 30 C
    # Grande saison pluies (Avr-Jul) : 28-31 C -> parfois acceptable
    # Petite saison seche  (Aou-Sep) : 27-28 C -> MEILLEURE periode
    # Petite saison pluies (Oct)     : 29-31 C
    temperature = np.array([
        np.random.uniform(29, 32) if s == 0 else
        np.random.uniform(28, 31) if s == 1 else
        np.random.uniform(27, 28) if s == 2 else
        np.random.uniform(29, 31)
        for s in saison_par_jour
    ])

    # -- HUMIDITE AIR ---------------------------------------------
    # Source : Wikipedia CI + WeatherSpark
    #
    # Grande saison seche  : 40-65%  -> souvent < 60% : bloque
    # Grande saison pluies : 75-100% -> souvent > 80% : optimal
    #                                   mais pluie bloque souvent
    # Petite saison seche  : 55-80%  -> plage acceptable/optimale
    # Petite saison pluies : 70-95%  -> souvent optimal
    humidite_air = np.array([
        np.random.uniform(40, 65)  if s == 0 else
        np.random.uniform(75, 100) if s == 1 else
        np.random.uniform(55, 80)  if s == 2 else
        np.random.uniform(70, 95)
        for s in saison_par_jour
    ])

    # -- VITESSE VENT (km/h) --------------------------------------
    # Harmattan en grande saison seche -> vents forts frequents
    # Source : Routard CI + SODEXAM
    #
    # Grande saison seche  : 3-35 km/h (harmattan)
    # Autres saisons       : 0-18 km/h
    vitesse_vent = np.array([
        np.random.uniform(3, 35) if s == 0 else
        np.random.uniform(0, 18)
        for s in saison_par_jour
    ])

    # -- PLUIE ----------------------------------------------------
    pluie = np.array([
        np.random.uniform(1, 35)
        if np.random.random() < probabilite_pluie(mois_par_jour[j])
        else 0.0
        for j in range(NB_JOURS)
    ])

    # -- PLUIE PREVUE 3H ------------------------------------------
    # Fenetre stricte de 3h (1/8e de probabilite journaliere)
    # Source : ARVALIS / Sencrop
    pluie_prevue_3h = np.array([
        1 if np.random.random() < probabilite_pluie(mois_par_jour[j]) / 8
        else 0
        for j in range(NB_JOURS)
    ])

    # ================================================================
    # RISQUES MALADIES
    # ================================================================

    # -- RISQUE POURRITURE BRUNE (Phytophthora palmivora) ---------
    # Actif : grande saison pluies (Avr-Jul) + petite saison pluies (Oct)
    # Condition : humidite_air > 75%
    # Source : Cahiers Agricultures 2024 / Yara CI
    risque_pourriture_brune = (
        (saison_par_jour == 1) |   # grande saison pluies
        (saison_par_jour == 3)     # petite saison pluies
    ) & (humidite_air > 75)

    # -- RISQUE MIRIDES (insectes capsides) -----------------------
    # Actif : grande saison seche (Nov-Mar) + petite saison seche (Aug-Sep)
    # Condition : temperature > 27 C
    # Source : Diallo 2023 / IRD / Organic Africa
    risque_mirides = (
        (saison_par_jour == 0) |   # grande saison seche
        (saison_par_jour == 2)     # petite saison seche
    ) & (temperature > 27)

    # Risque maladie present = au moins un des deux actif
    risque_maladie = (risque_pourriture_brune | risque_mirides)

    # ================================================================
    # CONDITIONS METEOROLOGIQUES FAVORABLES
    # ================================================================
    # Toutes les conditions doivent etre reunies
    # Sources : ARVALIS, Agrifind, Syngenta, BASF, Weenat

    conditions_favorables = (
        (temperature    <  30) &    # pas de phytotoxicite
        (humidite_air   >= 60) &    # absorption possible
        (humidite_air   <= 95) &    # pas de ruissellement
        (vitesse_vent   <  12) &    # pas de derive (ARVALIS)
        (pluie          == 0)  &    # produit non dilue
        (pluie_prevue_3h == 0)      # fenetre 3h disponible
    )

    # ================================================================
    # DECISION FINALE
    # ================================================================
    # PULVERISER si :
    # conditions meteo favorables ET risque maladie present
    pulveriser = (conditions_favorables & risque_maladie).astype(int)

    # ================================================================
    # CONSTRUCTION DU TABLEAU
    # ================================================================
    dataset = pd.DataFrame({
        "mois"                    : mois_par_jour,
        "saison"                  : saison_par_jour,
        "temperature"             : np.round(temperature, 1),
        "humidite_air"            : np.round(humidite_air, 1),
        "vitesse_vent"            : np.round(vitesse_vent, 1),
        "pluie"                   : np.round(pluie, 1),
        "pluie_prevue_3h"         : pluie_prevue_3h,
        "risque_pourriture_brune" : risque_pourriture_brune.astype(int),
        "risque_mirides"          : risque_mirides.astype(int),
        "pulveriser"              : pulveriser
    })

    # -- SAUVEGARDE -----------------------------------------------
    os.makedirs("data", exist_ok=True)
    dataset.to_csv("data/dataset_pesticide.csv", index=False)

    # -- STATISTIQUES ---------------------------------------------
    print(f"\nDataset genere      : {NB_JOURS} lignes")
    print(f"Fichier             : data/dataset_pesticide.csv")

    print(f"\nApercu des 5 premieres lignes :")
    print(dataset.head())

    print(f"\nStatistiques globales :")
    print(f"   Pulverisation necessaire : {pulveriser.sum()} "
          f"({pulveriser.mean()*100:.1f}%)")
    print(f"   Pas de pulverisation     : {NB_JOURS - pulveriser.sum()} "
          f"({(1-pulveriser.mean())*100:.1f}%)")

    print(f"\nDetail des blocages :")
    print(f"   Temperature  >= 30 C  : {(temperature  >= 30).sum()} jours")
    print(f"   Humidite air <  60%   : {(humidite_air <  60).sum()} jours")
    print(f"   Humidite air >  95%   : {(humidite_air >  95).sum()} jours")
    print(f"   Vent         >= 12 kh : {(vitesse_vent >= 12).sum()} jours")
    print(f"   Pluie en cours        : {(pluie > 0).sum()} jours")
    print(f"   Pluie prevue 3h       : {pluie_prevue_3h.sum()} jours")

    print(f"\nDetail des risques maladies :")
    print(f"   Risque pourriture brune : {risque_pourriture_brune.sum()} jours")
    print(f"   Risque mirides          : {risque_mirides.sum()} jours")
    print(f"   Aucun risque maladie    : {(~risque_maladie).sum()} jours")

    print(f"\nPulverisation par saison :")
    noms = [
        (0, "Grande saison seche  (Nov-Mar)"),
        (1, "Grande saison pluies (Avr-Jul)"),
        (2, "Petite saison seche  (Aou-Sep)"),
        (3, "Petite saison pluies (Oct)     "),
    ]
    for code, nom in noms:
        mask  = saison_par_jour == code
        total = mask.sum()
        pulv  = pulveriser[mask].sum()
        cond  = conditions_favorables[mask].sum()
        risq  = risque_maladie[mask].sum()
        print(f"   {nom} : {pulv}/{total} ({pulv/total*100:.1f}%)"
              f"  | cond OK : {cond} | risque : {risq}")


if __name__ == "__main__":
    generer_dataset()