import numpy as np
import os
import sys
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


# -- CONFIGURATION --------------------------------------------
IMG_SIZE        = 224
DOSSIER_MODEL   = "model"
CLASSES         = ["BLACKPOD", "FROSTYPOD", "HEALTHY", "MIRID"]

# Messages en français pour chaque classe
MESSAGES = {
    "HEALTHY"   : {
        "statut"  : "Cabosse saine",
        "action"  : "Aucun traitement necessaire",
        "couleur" : "green",
        "emoji"   : "✅"
    },
    "BLACKPOD"  : {
        "statut"  : "Pourriture brune detectee (Phytophthora palmivora)",
        "action"  : "Pulveriser fongicide dans les 24h",
        "couleur" : "red",
        "emoji"   : "🔴",
        "source"  : "Cahiers Agricultures 2024 / Yara CI"
    },
    "FROSTYPOD" : {
        "statut"  : "Moniliose detectee (Moniliophthora roreri)",
        "action"  : "Retirer et bruler les cabosses atteintes",
        "couleur" : "orange",
        "emoji"   : "🟠",
        "source"  : "ICCO / FAO"
    },
    "MIRID"     : {
        "statut"  : "Attaque mirides detectee (insectes capsides)",
        "action"  : "Pulveriser insecticide si conditions meteo OK",
        "couleur" : "purple",
        "emoji"   : "🟣",
        "source"  : "Diallo 2023 / IRD"
    }
}

# Seuil de confiance minimum pour valider une detection
SEUIL_CONFIANCE = 0.60


def charger_modele():
    """
    Charge le modele de detection des maladies.
    Essaie d'abord le format .keras puis .h5
    """
    chemin_keras = os.path.join(DOSSIER_MODEL, "modele_maladie.keras")
    chemin_h5    = os.path.join(DOSSIER_MODEL, "modele_maladie.h5")

    if os.path.exists(chemin_keras):
        print(f"Chargement modele : {chemin_keras}")
        return load_model(chemin_keras)
    elif os.path.exists(chemin_h5):
        print(f"Chargement modele : {chemin_h5}")
        return load_model(chemin_h5)
    else:
        print("ERREUR : Aucun modele trouve dans model/")
        print("Lance d'abord : python detection/train_modele.py")
        sys.exit(1)


def preparer_image(chemin_image):
    """
    Charge et prépare une image pour le modele.

    Preprocessing identique à l'entrainement :
    - Redimensionnement 224x224 (taille MobileNetV2)
    - Normalisation pixels 0-255 -> 0.0-1.0
    - Ajout dimension batch : (224,224,3) -> (1,224,224,3)
    """
    if not os.path.exists(chemin_image):
        print(f"ERREUR : Image introuvable : {chemin_image}")
        sys.exit(1)

    img        = image.load_img(chemin_image,
                                target_size=(IMG_SIZE, IMG_SIZE))
    img_array  = image.img_to_array(img)
    img_array  = img_array / 255.0
    img_array  = np.expand_dims(img_array, axis=0)

    return img, img_array


def analyser_image(modele, img_array):
    """
    Lance la prediction et retourne les probabilites
    pour chaque classe.
    """
    predictions  = modele.predict(img_array, verbose=0)
    probabilites = predictions[0]

    resultats = {
        CLASSES[i]: float(probabilites[i])
        for i in range(len(CLASSES))
    }

    # Classe avec la probabilite la plus haute
    idx_max      = np.argmax(probabilites)
    classe_pred  = CLASSES[idx_max]
    confiance    = float(probabilites[idx_max])

    return classe_pred, confiance, resultats


def afficher_resultats(chemin_image, classe_pred,
                       confiance, resultats, img):
    """
    Affiche l'image et les résultats de détection
    dans une fenêtre graphique.
    """
    info    = MESSAGES[classe_pred]
    couleur = info["couleur"]

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor("#1a1a2e")

    # -- IMAGE ------------------------------------------------
    axes[0].imshow(img)
    axes[0].set_title(
        f"{info['emoji']} {info['statut']}",
        color=couleur, fontsize=13, fontweight="bold", pad=10
    )
    axes[0].axis("off")

    # Bordure colorée selon la maladie
    for spine in axes[0].spines.values():
        spine.set_edgecolor(couleur)
        spine.set_linewidth(3)

    # -- GRAPHIQUE PROBABILITES -------------------------------
    couleurs_barres = []
    for c in CLASSES:
        if c == classe_pred:
            couleurs_barres.append(couleur)
        else:
            couleurs_barres.append("#555555")

    barres = axes[1].barh(
        CLASSES,
        [resultats[c] * 100 for c in CLASSES],
        color=couleurs_barres,
        edgecolor="white",
        linewidth=0.5
    )

    # Valeurs sur les barres
    for barre, classe in zip(barres, CLASSES):
        valeur = resultats[classe] * 100
        axes[1].text(
            valeur + 1, barre.get_y() + barre.get_height() / 2,
            f"{valeur:.1f}%",
            va="center", ha="left",
            color="white", fontsize=11, fontweight="bold"
        )

    axes[1].set_xlim(0, 115)
    axes[1].set_xlabel("Probabilite (%)", color="white")
    axes[1].set_title(
        "Analyse par classe",
        color="white", fontsize=13, fontweight="bold"
    )
    axes[1].set_facecolor("#16213e")
    axes[1].tick_params(colors="white")
    axes[1].spines["bottom"].set_color("#555555")
    axes[1].spines["top"].set_visible(False)
    axes[1].spines["right"].set_visible(False)
    axes[1].spines["left"].set_color("#555555")

    # Ligne seuil de confiance
    axes[1].axvline(
        x=SEUIL_CONFIANCE * 100,
        color="yellow", linestyle="--",
        linewidth=1.5, alpha=0.7,
        label=f"Seuil confiance {SEUIL_CONFIANCE*100:.0f}%"
    )
    axes[1].legend(
        loc="lower right",
        facecolor="#1a1a2e",
        labelcolor="yellow",
        fontsize=9
    )

    # -- TITRE PRINCIPAL --------------------------------------
    statut_confiance = (
        "DETECTION FIABLE" if confiance >= SEUIL_CONFIANCE
        else "CONFIANCE INSUFFISANTE — verifier manuellement"
    )

    fig.suptitle(
        f"CACAO INTELLIGENT — Detection Maladie\n"
        f"{statut_confiance} | Confiance : {confiance*100:.1f}%",
        color="white", fontsize=14, fontweight="bold", y=1.02
    )

    plt.tight_layout()
    plt.savefig(
        "detection/resultat_analyse.png",
        bbox_inches="tight",
        facecolor=fig.get_facecolor()
    )
    print("Graphique sauvegarde : detection/resultat_analyse.png")
    plt.show()


def afficher_recommandation(classe_pred, confiance):
    """
    Affiche la recommandation finale dans le terminal.
    """
    info = MESSAGES[classe_pred]

    print("\n" + "=" * 55)
    print("   RESULTAT DE L'ANALYSE")
    print("=" * 55)
    print(f"   Maladie detectee : {info['emoji']} {info['statut']}")
    print(f"   Confiance        : {confiance*100:.1f}%")
    print(f"   Action           : {info['action']}")

    if "source" in info:
        print(f"   Source           : {info['source']}")

    print()

    if confiance < SEUIL_CONFIANCE:
        print(f"   ⚠️  ATTENTION : Confiance < {SEUIL_CONFIANCE*100:.0f}%")
        print(f"   Recommandation  : Prendre une nouvelle photo")
        print(f"   Conseils        :")
        print(f"      - Cadrer uniquement la cabosse")
        print(f"      - Bonne luminosite (pas d'ombre)")
        print(f"      - Distance 20-30cm de la cabosse")
    else:
        print(f"   ✅ Detection fiable — action recommandee confirmee")

    print("=" * 55)


def tester_depuis_dataset():
    """
    Teste le modele sur des images du dataset de test
    pour chaque classe — utile si pas d'image personnelle.
    """
    print("\nAucune image fournie — test depuis le dataset...")
    print("Recherche d'une image par classe dans detection/dataset/test/\n")

    dossier_test = "detection/dataset/test"

    if not os.path.exists(dossier_test):
        print("Dataset test introuvable.")
        return

    for classe in CLASSES:
        dossier_classe = os.path.join(dossier_test, classe)
        if not os.path.exists(dossier_classe):
            continue

        images = [
            f for f in os.listdir(dossier_classe)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ]

        if not images:
            continue

        chemin = os.path.join(dossier_classe, images[0])
        print(f"--- Test classe : {classe} ---")
        print(f"    Image : {images[0]}")

        modele          = charger_modele()
        img, img_array  = preparer_image(chemin)
        classe_pred, confiance, resultats = analyser_image(
            modele, img_array
        )

        attendu  = classe
        correct  = "✅ CORRECT" if classe_pred == attendu else "❌ ERREUR"
        print(f"    Attendu  : {attendu}")
        print(f"    Obtenu   : {classe_pred} ({confiance*100:.1f}%)")
        print(f"    Resultat : {correct}\n")


# -- PROGRAMME PRINCIPAL --------------------------------------
if __name__ == "__main__":

    print("=" * 55)
    print("   CACAO INTELLIGENT — Testeur Detection Maladie")
    print("=" * 55)

    # Usage : python detection/tester_modele.py [chemin_image]
    # Sans argument -> test automatique depuis dataset

    if len(sys.argv) > 1:
        # Image fournie en argument
        chemin_image = sys.argv[1]
        print(f"Image analysee : {chemin_image}")

        modele = charger_modele()
        img, img_array = preparer_image(chemin_image)
        classe_pred, confiance, resultats = analyser_image(
            modele, img_array
        )

        afficher_recommandation(classe_pred, confiance)
        afficher_resultats(
            chemin_image, classe_pred,
            confiance, resultats, img
        )

    else:
        # Pas d'image -> test automatique depuis dataset
        tester_depuis_dataset()