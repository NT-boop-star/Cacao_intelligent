import os
import shutil
import pandas as pd


def reorganiser_split(split):
    """
    Lit le CSV d'un split et déplace chaque image
    dans le sous-dossier correspondant à sa classe.
    """
    dossier_split = f"detection/dataset/{split}"
    csv_path      = os.path.join(dossier_split, "_classes.csv")

    if not os.path.exists(csv_path):
        print(f"   CSV introuvable : {csv_path}")
        return

    df      = pd.read_csv(csv_path)
    classes = [c for c in df.columns if c != "filename"]

    print(f"\n   Split : {split}")
    print(f"   Classes trouvees : {classes}")
    print(f"   Images a traiter : {len(df)}")

    # Crée les sous-dossiers par classe
    for classe in classes:
        chemin_classe = os.path.join(dossier_split, classe)
        os.makedirs(chemin_classe, exist_ok=True)

    # Déplace chaque image dans son dossier de classe
    deplaces  = 0
    ignores   = 0
    multi     = 0

    for _, ligne in df.iterrows():
        nom_fichier = ligne["filename"]
        source      = os.path.join(dossier_split, nom_fichier)

        # Trouve la classe (colonne avec valeur 1)
        labels_actifs = [
            c for c in classes if ligne[c] == 1
        ]

        if not os.path.exists(source):
            ignores += 1
            continue

        if len(labels_actifs) == 0:
            # Pas de label -> ignorer
            ignores += 1
            continue

        if len(labels_actifs) > 1:
            # Multi-label -> prendre le premier
            multi += 1

        classe_choisie   = labels_actifs[0]
        destination      = os.path.join(
            dossier_split, classe_choisie, nom_fichier
        )

        shutil.move(source, destination)
        deplaces += 1

    print(f"   Images deplacees  : {deplaces}")
    print(f"   Multi-label       : {multi}")
    print(f"   Ignorees          : {ignores}")

    # Statistiques par classe
    print(f"   Repartition :")
    for classe in classes:
        chemin_classe = os.path.join(dossier_split, classe)
        nb            = len(os.listdir(chemin_classe))
        print(f"      {classe:20} : {nb} images")


def main():
    print("=" * 55)
    print("   PREPARATION DATASET — REORGANISATION PAR CLASSE")
    print("=" * 55)
    print("Lecture CSV -> creation dossiers par classe")
    print("Sources : BLACKPOD / FROSTYPOD / HEALTHY / MIRID")
    print("=" * 55)

    for split in ["train", "valid", "test"]:
        reorganiser_split(split)

    print("\n" + "=" * 55)
    print("   Dataset pret pour l'entrainement !")
    print("=" * 55)


if __name__ == "__main__":
    main()