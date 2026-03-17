import os
import shutil
import pandas as pd

CLASSES_VALIDES = ["BLACKPOD", "FROSTYPOD", "HEALTHY", "MIRID"]

def fusionner_split(split):
    source_split = f"detection/nyarko_temp/{split}"
    dest_split   = f"detection/dataset/{split}"
    csv_path     = os.path.join(source_split, "_classes.csv")

    if not os.path.exists(csv_path):
        print(f"   CSV introuvable : {csv_path}")
        return

    df      = pd.read_csv(csv_path)
    classes = [c for c in df.columns if c != "filename"]

    print(f"\n   Split : {split}")
    print(f"   Classes trouvees : {classes}")
    print(f"   Images a traiter : {len(df)}")

    ajoutes  = 0
    ignores  = 0
    doublons = 0

    for _, ligne in df.iterrows():
        nom_fichier   = ligne["filename"]
        source_image  = os.path.join(source_split, nom_fichier)

        # Trouver la classe
        labels_actifs = [c for c in classes if ligne[c] == 1]

        if not os.path.exists(source_image):
            ignores += 1
            continue

        if len(labels_actifs) == 0:
            ignores += 1
            continue

        classe = labels_actifs[0].upper().strip()

        if classe not in CLASSES_VALIDES:
            ignores += 1
            continue

        # Dossier destination
        dossier_dest = os.path.join(dest_split, classe)
        os.makedirs(dossier_dest, exist_ok=True)

        # Prefixer pour eviter doublons
        dest_image = os.path.join(dossier_dest, f"nyarko_{nom_fichier}")

        if os.path.exists(dest_image):
            doublons += 1
            continue

        shutil.copy2(source_image, dest_image)
        ajoutes += 1

    print(f"   Ajoutes  : {ajoutes}")
    print(f"   Doublons : {doublons}")
    print(f"   Ignores  : {ignores}")

    # Bilan par classe
    print(f"   Repartition apres fusion :")
    for classe in CLASSES_VALIDES:
        dossier = os.path.join(dest_split, classe)
        nb = len(os.listdir(dossier)) if os.path.exists(dossier) else 0
        print(f"      {classe:12} : {nb} images")


def main():
    print("=" * 55)
    print("   FUSION NYARKO -> DATASET EXISTANT")
    print("=" * 55)

    for split in ["train", "valid", "test"]:
        fusionner_split(split)

    print("\n" + "=" * 55)
    print("Dataset total apres fusion :")
    total = 0
    for split in ["train", "valid", "test"]:
        for classe in CLASSES_VALIDES:
            dossier = f"detection/dataset/{split}/{classe}"
            nb = len(os.listdir(dossier)) if os.path.exists(dossier) else 0
            total += nb
    print(f"Total images : {total}")
    print("=" * 55)

if __name__ == "__main__":
    main()