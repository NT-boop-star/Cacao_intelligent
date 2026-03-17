import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import pickle
import os


def charger_donnees():
    """
    Charge le dataset pesticide et le prepare pour l'entrainement.

    Features utilisees :
    - mois              : contexte saisonnier (1-12)
    - saison            : code saison CI (0-3)
    - temperature       : WeatherSpark CI (27-32 C selon saison)
    - humidite_air      : Wikipedia CI (40-95% selon saison)
    - vitesse_vent      : km/h (harmattan en saison seche)
    - pluie             : mm (SODEXAM)
    - pluie_prevue_3h   : fenetre 3h apres traitement (ARVALIS)
    - risque_pourriture : champignon Phytophthora (Cahiers Agri 2024)
    - risque_mirides    : insectes capsides (Diallo 2023 / IRD)

    Cible : pulveriser (0 ou 1)
    """

    print("Chargement du dataset pesticide...")

    dataset = pd.read_csv("data/dataset_pesticide.csv")

    X = dataset[[
        "mois",
        "saison",
        "temperature",
        "humidite_air",
        "vitesse_vent",
        "pluie",
        "pluie_prevue_3h",
        "risque_pourriture_brune",
        "risque_mirides"
    ]]

    y = dataset["pulveriser"]

    print(f"Dataset charge      : {len(dataset)} lignes")
    print(f"Colonnes d'entree   : {list(X.columns)}")
    print(f"Colonne cible       : pulveriser (0 ou 1)")
    print(f"Pulverisations      : {y.sum()} ({y.mean()*100:.1f}%)")

    return X, y


def entrainer_modele(X, y):
    """
    Divise les donnees et entraine le modele Random Forest
    """

    print("\nDivision train/test...")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42
    )

    print(f"   Donnees entrainement : {len(X_train)} lignes")
    print(f"   Donnees test         : {len(X_test)} lignes")

    print("\nEntrainement du modele Random Forest...")

    modele = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42
    )

    modele.fit(X_train, y_train)
    print("Modele entraine avec succes !")

    return modele, X_test, y_test


def evaluer_modele(modele, X_test, y_test):
    """
    Evalue les performances du modele sur les donnees de test
    """

    print("\nEvaluation du modele...")

    y_pred = modele.predict(X_test)

    print("\nRapport de performance :")
    print(classification_report(
        y_test, y_pred,
        target_names=["Pas pulverisation", "Pulverisation"]
    ))

    matrice = confusion_matrix(y_test, y_pred)
    print("Matrice de confusion :")
    print(f"   Vrais negatifs  (0 predit 0) : {matrice[0][0]}")
    print(f"   Faux positifs   (0 predit 1) : {matrice[0][1]}")
    print(f"   Faux negatifs   (1 predit 0) : {matrice[1][0]}")
    print(f"   Vrais positifs  (1 predit 1) : {matrice[1][1]}")


def afficher_importance(modele, X):
    """
    Affiche quelles variables influencent le plus la decision
    """

    print("\nImportance des variables :")

    importances = modele.feature_importances_
    colonnes    = X.columns
    indices     = np.argsort(importances)[::-1]

    for idx in indices:
        barre = "|" * int(importances[idx] * 50)
        print(f"   {colonnes[idx]:25} : {barre} ({importances[idx]:.3f})")


def sauvegarder_modele(modele):
    """
    Sauvegarde le modele entraine dans un fichier .pkl
    """

    os.makedirs("model", exist_ok=True)
    chemin = "model/modele_pesticide.pkl"

    with open(chemin, "wb") as f:
        pickle.dump(modele, f)

    print(f"\nModele sauvegarde : {chemin}")


def tester_prediction(modele):
    """
    Test avec des cas concrets couvrant les 4 saisons CI.
    Chaque cas verifie une situation agronomique reelle.
    """

    print("\nTest de prédiction en direct :")

    cas = [
        {
            "description" : "Aout | 27C, humidite 72%, vent 5 km/h, "
                            "pas pluie, risque mirides",
            "attendu"     : 1,
            "donnees"     : {
                "mois": 8, "saison": 2,
                "temperature": 27.5, "humidite_air": 72.0,
                "vitesse_vent": 5.0, "pluie": 0.0,
                "pluie_prevue_3h": 0,
                "risque_pourriture_brune": 0,
                "risque_mirides": 1
            }
        },
        {
            "description" : "Juin | 29C, humidite 85%, vent 8 km/h, "
                            "pluie en cours, risque pourriture",
            "attendu"     : 0,
            "donnees"     : {
                "mois": 6, "saison": 1,
                "temperature": 29.0, "humidite_air": 85.0,
                "vitesse_vent": 8.0, "pluie": 12.0,
                "pluie_prevue_3h": 1,
                "risque_pourriture_brune": 1,
                "risque_mirides": 0
            }
        },
        {
            "description" : "Janvier | 31C, humidite 48%, vent 22 km/h, "
                            "pas pluie, risque mirides",
            "attendu"     : 0,
            "donnees"     : {
                "mois": 1, "saison": 0,
                "temperature": 31.0, "humidite_air": 48.0,
                "vitesse_vent": 22.0, "pluie": 0.0,
                "pluie_prevue_3h": 0,
                "risque_pourriture_brune": 0,
                "risque_mirides": 1
            }
        },
        {
            "description" : "Septembre | 28C, humidite 65%, vent 6 km/h, "
                            "pas pluie, risque mirides",
            "attendu"     : 1,
            "donnees"     : {
                "mois": 9, "saison": 2,
                "temperature": 28.0, "humidite_air": 65.0,
                "vitesse_vent": 6.0, "pluie": 0.0,
                "pluie_prevue_3h": 0,
                "risque_pourriture_brune": 0,
                "risque_mirides": 1
            }
        },
        {
            "description" : "Mai | 29C, humidite 88%, vent 4 km/h, "
                            "pas pluie, risque pourriture",
            "attendu"     : 1,
            "donnees"     : {
                "mois": 5, "saison": 1,
                "temperature": 29.0, "humidite_air": 88.0,
                "vitesse_vent": 4.0, "pluie": 0.0,
                "pluie_prevue_3h": 0,
                "risque_pourriture_brune": 1,
                "risque_mirides": 0
            }
        },
        {
            "description" : "Aout | 27C, humidite 70%, vent 5 km/h, "
                            "pluie prevue dans 3h, risque mirides",
            "attendu"     : 0,
            "donnees"     : {
                "mois": 8, "saison": 2,
                "temperature": 27.0, "humidite_air": 70.0,
                "vitesse_vent": 5.0, "pluie": 0.0,
                "pluie_prevue_3h": 1,
                "risque_pourriture_brune": 0,
                "risque_mirides": 1
            }
        },
    ]

    tous_ok = True
    for c in cas:
        df       = pd.DataFrame([c["donnees"]])
        pred     = int(modele.predict(df)[0])
        resultat = "PULVERISER" if pred == 1 else "NE PAS PULVERISER"
        attendu  = "PULVERISER" if c["attendu"] == 1 else "NE PAS PULVERISER"
        ok       = "OK" if pred == c["attendu"] else "ERREUR"
        if ok == "ERREUR":
            tous_ok = False
        print(f"   {c['description']}")
        print(f"   Attendu : {attendu} | Obtenu : {resultat} [{ok}]\n")

    if tous_ok:
        print("   Tous les tests sont corrects !")
    else:
        print("   Certains tests ont echoue — verifier le modele.")


# -- PROGRAMME PRINCIPAL --------------------------------------
if __name__ == "__main__":

    print("=" * 55)
    print("   MODELE IA - PULVERISATION PESTICIDES CACAO")
    print("=" * 55)

    X, y                   = charger_donnees()
    modele, X_test, y_test = entrainer_modele(X, y)
    evaluer_modele(modele, X_test, y_test)
    afficher_importance(modele, X)
    sauvegarder_modele(modele)
    tester_prediction(modele)

    print("=" * 55)
    print("   Modele pret a etre utilise !")
    print("=" * 55)