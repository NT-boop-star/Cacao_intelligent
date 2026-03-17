import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os

# -- CHARGER LE MODELE SAUVEGARDE ----------------------------
CHEMIN_MODELE = "model/modele_maladie.keras"
DOSSIER_TEST  = "detection/dataset/test"
IMG_SIZE      = 224
BATCH_SIZE    = 32

modele = load_model(CHEMIN_MODELE)
print("Modele charge")

# -- CHARGER UNIQUEMENT LE DATASET TEST ----------------------
# Aucun entrainement — lecture seule
test_gen = ImageDataGenerator(rescale=1./255)

test_data = test_gen.flow_from_directory(
    DOSSIER_TEST,
    target_size = (IMG_SIZE, IMG_SIZE),
    batch_size  = BATCH_SIZE,
    class_mode  = "categorical",
    shuffle     = False   # important pour les métriques
)

# -- EVALUATION EN UNE LIGNE ---------------------------------
print("\nEvaluation en cours...")
loss, accuracy = modele.evaluate(test_data, verbose=1)

print(f"\nResultat final :")
print(f"  Accuracy : {accuracy*100:.2f}%")
print(f"  Loss     : {loss:.4f}")