import os
import numpy as np
from tensorflow.keras.models import load_model
from PIL import Image

DOSSIER_TEST = "detection/dataset/test/HEALTHY"
MODELE_PATH  = "model/modele_maladie.keras"
IMG_SIZE     = 224
CLASSES      = ["BLACKPOD", "FROSTYPOD", "HEALTHY", "MIRID"]

modele = load_model(MODELE_PATH)
print(f"Modele charge — test de toutes les images HEALTHY...\n")

correct  = 0
erreurs  = []

images = os.listdir(DOSSIER_TEST)
total  = len(images)

for i, nom in enumerate(images):
    chemin = os.path.join(DOSSIER_TEST, nom)
    img    = Image.open(chemin).convert("RGB").resize((IMG_SIZE, IMG_SIZE))
    arr    = np.expand_dims(np.array(img) / 255.0, axis=0)

    probas    = modele.predict(arr, verbose=0)[0]
    idx       = np.argmax(probas)
    classe    = CLASSES[idx]
    confiance = probas[idx] * 100

    if classe == "HEALTHY":
        correct += 1
    else:
        erreurs.append((nom, classe, round(confiance, 1)))

    if (i+1) % 50 == 0:
        print(f"  Progression : {i+1}/{total}")

print(f"\n{'='*50}")
print(f"RESULTATS HEALTHY ({total} images)")
print(f"{'='*50}")
print(f"Correctes : {correct}/{total} ({correct/total*100:.1f}%)")
print(f"Erreurs   : {len(erreurs)}/{total} ({len(erreurs)/total*100:.1f}%)")

if erreurs:
    print(f"\nDetail erreurs :")
    from collections import Counter
    confusion = Counter([e[1] for e in erreurs])
    for classe, nb in confusion.items():
        print(f"  HEALTHY -> {classe} : {nb} fois")