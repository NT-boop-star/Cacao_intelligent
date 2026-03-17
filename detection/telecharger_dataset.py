import os
from roboflow import Roboflow


def telecharger_dataset():
    """
    Télécharge le dataset de détection des maladies du cacao
    depuis Roboflow.

    Dataset : COCOA DISEASE DETECTION — myworkspace
    Source  : Roboflow Universe (Novembre 2024)
    Images  : 3087 images
    URL     : https://universe.roboflow.com/myworkspace-2lslx/
              cocoa-disease-detection-ysgtm-tdjha
    """

    print("=" * 55)
    print("   TELECHARGEMENT DATASET MALADIES CACAO")
    print("=" * 55)
    print("Source  : Roboflow — myworkspace (Nov 2024)")
    print("Images  : 3087 images")
    print("=" * 55)

    # -- REMPLACE ICI PAR TA CLE ROBOFLOW --------------------
    from dotenv import load_dotenv
    load_dotenv()
    API_KEY = os.environ.get("ROBOFLOW_API_KEY", "VOTRE_CLE_ROBOFLOW")
    DOSSIER = "detection/dataset"

    print("\nConnexion a Roboflow...")

    try:
        rf      = Roboflow(api_key=API_KEY)
        project = rf.workspace("myworkspace-2lslx") \
                    .project("cocoa-disease-detection-ysgtm-tdjha")
        version = project.version(1)

        print(f"Projet trouve : {project.name}")
        print(f"Telechargement -> {DOSSIER} ...")

        version.download("multiclass", location=DOSSIER)

        print(f"\nDataset telecharge avec succes !")

        # -- VERIFICATION STRUCTURE --------------------------
        print("\nVerification de la structure :")
        for split in ["train", "valid", "test"]:
            chemin = os.path.join(DOSSIER, split)
            if os.path.exists(chemin):
                classes = [
                    c for c in os.listdir(chemin)
                    if os.path.isdir(os.path.join(chemin, c))
                ]
                total = sum(
                    len(os.listdir(os.path.join(chemin, c)))
                    for c in classes
                )
                print(f"   {split:5} : {total} images "
                      f"— classes : {classes}")

    except Exception as e:
        print(f"\nErreur : {e}")
        print("\nSolution manuelle :")
        print("1. Va sur https://universe.roboflow.com/myworkspace-2lslx/")
        print("   cocoa-disease-detection-ysgtm-tdjha")
        print("2. Download -> folder -> download zip")
        print("3. Extrais dans detection/dataset/")


if __name__ == "__main__":
    telecharger_dataset()
