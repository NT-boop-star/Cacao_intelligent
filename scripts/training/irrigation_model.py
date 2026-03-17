import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import pickle
import os


def charger_donnees():
    """
    Charge le dataset et le prépare pour l'entraînement.
    Inclut mois et saison pour la conscience saisonnière.
    """

    print("Chargement du dataset...")

    dataset = pd.read_csv("data/dataset.csv")

    # X = ce que l'IA observe
    # mois et saison ajoutés pour distinguer les saisons CI
    X = dataset[[
        "mois",
        "saison",
        "temperature",
        "humidite_air",
        "humidite_sol",
        "vitesse_vent",
        "pluie",
        "pluie_prevue"
    ]]

    # y = ce que l'IA doit prédire
    y = dataset["irrigation"]

    print(f"Dataset chargé : {len(dataset)} lignes")
    print(f"Colonnes d'entrée  : {list(X.columns)}")
    print(f"Colonne cible      : irrigation (0 ou 1)")

    return X, y


def entrainer_modele(X, y):
    """
    Divise les données et entraîne le modèle Random Forest
    """

    print("\nDivision train/test...")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42
    )

    print(f"   Données entraînement : {len(X_train)} lignes")
    print(f"   Données test         : {len(X_test)} lignes")

    print("\nEntraînement du modèle Random Forest...")

    modele = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42
    )

    modele.fit(X_train, y_train)

    print("Modèle entraîné avec succès !")

    return modele, X_test, y_test


def evaluer_modele(modele, X_test, y_test):
    """
    Evalue les performances du modèle sur les données de test
    """

    print("\nEvaluation du modèle...")

    y_pred = modele.predict(X_test)

    print("\nRapport de performance :")
    print(classification_report(
        y_test, y_pred,
        target_names=["Pas irrigation", "Irrigation"]
    ))

    matrice = confusion_matrix(y_test, y_pred)
    print("Matrice de confusion :")
    print(f"   Vrais negatifs  (0 predit 0) : {matrice[0][0]}")
    print(f"   Faux positifs   (0 predit 1) : {matrice[0][1]}")
    print(f"   Faux negatifs   (1 predit 0) : {matrice[1][0]}")
    print(f"   Vrais positifs  (1 predit 1) : {matrice[1][1]}")

    return y_pred


def afficher_importance(modele, X):
    """
    Affiche quelles variables influencent le plus la décision
    """

    print("\nImportance des variables :")

    importances = modele.feature_importances_
    colonnes    = X.columns
    indices     = np.argsort(importances)[::-1]

    for idx in indices:
        barre = "|" * int(importances[idx] * 50)
        print(f"   {colonnes[idx]:15} : {barre} ({importances[idx]:.3f})")


def sauvegarder_modele(modele):
    """
    Sauvegarde le modèle entraîné dans un fichier .pkl
    pour éviter de réentraîner à chaque démarrage
    """

    os.makedirs("model", exist_ok=True)
    chemin = "model/modele_irrigation.pkl"

    with open(chemin, "wb") as f:
        pickle.dump(modele, f)

    print(f"\nModèle sauvegardé : {chemin}")


def tester_prediction(modele):

    print("\nTest de prédiction en direct :")

    cas = [
        {
            "description" : "Janvier  | sol sec (25%), 32C, harmattan, pas de pluie",
            "attendu"     : 1,
            "donnees"     : {"mois": 1,  "saison": 0, "temperature": 32.0,
                             "humidite_air": 50.0, "humidite_sol": 25.0,
                             "vitesse_vent": 15.0, "pluie": 0.0, "pluie_prevue": 0}
        },
        {
            "description" : "Juin     | sol humide (70%), pluie en cours",
            "attendu"     : 0,
            "donnees"     : {"mois": 6,  "saison": 1, "temperature": 27.0,
                             "humidite_air": 90.0, "humidite_sol": 70.0,
                             "vitesse_vent": 5.0,  "pluie": 15.0, "pluie_prevue": 1}
        },
        {
            "description" : "Aout     | sol sec (35%), 30C, petite saison seche",
            "attendu"     : 1,
            "donnees"     : {"mois": 8,  "saison": 2, "temperature": 30.0,
                             "humidite_air": 60.0, "humidite_sol": 35.0,
                             "vitesse_vent": 10.0, "pluie": 0.0, "pluie_prevue": 0}
        },
        {
            "description" : "Janvier  | sol sec (28%), pluie prevue demain",
            "attendu"     : 0,
            "donnees"     : {"mois": 1,  "saison": 0, "temperature": 33.0,
                             "humidite_air": 45.0, "humidite_sol": 28.0,
                             "vitesse_vent": 20.0, "pluie": 0.0, "pluie_prevue": 1}
        },
        {
            "description" : "Octobre  | sol sec (38%), pas de pluie ni prevue",
            "attendu"     : 1,
            "donnees"     : {"mois": 10, "saison": 3, "temperature": 29.0,
                             "humidite_air": 68.0, "humidite_sol": 38.0,
                             "vitesse_vent": 8.0,  "pluie": 0.0, "pluie_prevue": 0}
        },
    ]

    tous_ok = True
    for c in cas:
        df      = pd.DataFrame([c["donnees"]])
        pred    = int(modele.predict(df)[0])
        resultat = "IRRIGUER" if pred == 1 else "NE PAS IRRIGUER"
        attendu  = "IRRIGUER" if c["attendu"] == 1 else "NE PAS IRRIGUER"
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
    print("   MODELE IA - IRRIGATION PREDICTIVE CACAO v3")
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