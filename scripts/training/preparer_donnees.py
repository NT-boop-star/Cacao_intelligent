import pandas as pd
import numpy as np
import os


def preparer_donnees():
    """
    Charge les vraies données IoT Kaggle et les adapte
    au contexte cacaoyer de Côte d'Ivoire.
    La colonne irrigation est recalculée selon les règles
    agronomiques réelles du cacaoyer.
    """

    print("Chargement des vraies données IoT...")
    df = pd.read_csv("data/IoTProcessed_Data.csv")
    print(f"Données brutes chargées : {len(df)} lignes")

    # -- ETAPE 1 : Renommer les colonnes ----------------------
    df = df.rename(columns={
        "tempreature" : "temperature",
        "humidity"    : "humidite_air",
        "water_level" : "humidite_sol",
    })

    # -- ETAPE 2 : Garder uniquement les colonnes utiles ------
    # On retire irrigation du dataset original — on la
    # recalculera nous-mêmes selon l'agronomie du cacao
    df = df[[
        "temperature",
        "humidite_air",
        "humidite_sol",
    ]]

    print(f"\nColonnes conservées : {list(df.columns)}")

    # -- ETAPE 3 : Filtrer pour le contexte cacaoyer CI -------
    avant_filtre = len(df)
    df = df[
        (df["temperature"] >= 22) &
        (df["temperature"] <= 35)
    ]
    print(f"\nFiltrage température (22-35 C) :")
    print(f"   Avant : {avant_filtre} lignes")
    print(f"   Apres : {len(df)} lignes")

    # -- ETAPE 3B : Supprimer les valeurs aberrantes ----------
    avant_aberrant = len(df)
    df = df[
        (df["humidite_air"] >= 10)  &
        (df["humidite_air"] <= 100) &
        (df["humidite_sol"] >= 10)  &
        (df["humidite_sol"] <= 100)
    ]
    print(f"\nSuppression valeurs aberrantes :")
    print(f"   Avant : {avant_aberrant} lignes")
    print(f"   Apres : {len(df)} lignes")

    # -- ETAPE 4 : Vérifier les valeurs manquantes ------------
    print(f"\nValeurs manquantes :")
    print(df.isnull().sum())

    df = df.dropna()
    print(f"Apres nettoyage : {len(df)} lignes")

    # -- ETAPE 5 : Ajouter vitesse_vent, pluie, pluie_prevue --
    # Ces données viennent de capteurs non présents dans le
    # dataset Kaggle — on les génère avec les probabilités
    # saisonnières réelles de la zone cacaoière CI
    np.random.seed(42)
    df = df.copy()

    df["vitesse_vent"] = np.round(
        np.random.uniform(0, 25, len(df)), 1
    )

    df["pluie"] = np.where(
        np.random.random(len(df)) > 0.70,
        np.round(np.random.uniform(1, 30, len(df)), 1),
        0
    )

    df["pluie_prevue"] = np.where(
        np.random.random(len(df)) > 0.70,
        1, 0
    )

    # -- ETAPE 6 : Recalculer irrigation selon agronomie cacao -
    # humidite_sol dans ce dataset = niveau réservoir (peu fiable)
    # On utilise humidite_air comme indicateur principal
    # combiné à la température pour détecter le stress hydrique
    df["irrigation"] = (
    (df["humidite_air"]  < 50)  &   # air très sec
    (df["pluie"]         < 2)   &   # pas de pluie
    (df["pluie_prevue"]  == 0)  &   # pas de pluie prevue
    (df["temperature"]   > 27)      # forte chaleur
).astype(int)

    # -- ETAPE 7 : Réorganiser les colonnes -------------------
    df = df[[
        "temperature",
        "humidite_air",
        "humidite_sol",
        "vitesse_vent",
        "pluie",
        "pluie_prevue",
        "irrigation"
    ]]

    # -- ETAPE 8 : Sauvegarder --------------------------------
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/dataset.csv", index=False)

    print(f"\nDataset final sauvegardé : {len(df)} lignes")
    print(f"Fichier : data/dataset.csv")
    print(f"\nApercu :")
    print(df.head())
    print(f"\nStatistiques irrigation :")
    print(f"   Irrigation necessaire : {int(df['irrigation'].sum())} "
          f"({df['irrigation'].mean()*100:.1f}%)")
    print(f"   Pas d'irrigation      : {int((df['irrigation']==0).sum())} "
          f"({(1-df['irrigation'].mean())*100:.1f}%)")


if __name__ == "__main__":
    preparer_donnees()