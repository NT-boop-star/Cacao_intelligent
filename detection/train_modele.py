import os
import shutil
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import (
    Dense, GlobalAveragePooling2D, Dropout, BatchNormalization
)
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import (
    EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
)
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.utils.class_weight import compute_class_weight


# -- CONFIGURATION --------------------------------------------
IMG_SIZE   = 224
BATCH_SIZE = 16      # Reduit de 32 -> 16 (meilleure convergence CPU)
EPOCHS     = 40
LR         = 0.0001

DOSSIER_DATASET = "detection/dataset"
DOSSIER_MODEL   = "model"
CLASSES         = ["BLACKPOD", "FROSTYPOD", "HEALTHY", "MIRID"]


def fusionner_classes():
    """
    Fusionne busukbuah-monilia dans BLACKPOD.
    busukbuah-monilia = pourriture cabosse en malais
    = même maladie que BLACKPOD (Phytophthora palmivora)
    Source : ICCO / Cahiers Agricultures 2024
    """
    print("Fusion busukbuah-monilia -> BLACKPOD ...")
    fusionne = False

    for split in ["train", "valid", "test"]:
        source = os.path.join(DOSSIER_DATASET, split, "busukbuah-monilia")
        dest   = os.path.join(DOSSIER_DATASET, split, "BLACKPOD")

        if not os.path.exists(source):
            continue

        fusionne = True
        os.makedirs(dest, exist_ok=True)
        images = os.listdir(source)

        for img in images:
            shutil.move(
                os.path.join(source, img),
                os.path.join(dest, img)
            )

        shutil.rmtree(source)
        print(f"   {split:5} : {len(images)} images fusionnees")

    if not fusionne:
        print("   Deja fusionne precedemment.")
    print("Fusion terminee !\n")


def calculer_poids_classes(train_data):
    """
    Calcule les poids par classe pour corriger le déséquilibre.

    FROSTYPOD n'a que 252 images vs 694 pour HEALTHY
    -> Sans correction le modele ignore FROSTYPOD
    -> Avec poids : erreur sur FROSTYPOD penalisee davantage

    Source : scikit-learn compute_class_weight documentation
    """
    print("Calcul des poids par classe...")

    labels   = train_data.classes
    classes  = np.unique(labels)

    poids = compute_class_weight(
        class_weight = "balanced",
        classes      = classes,
        y            = labels
    )

    poids_dict = dict(zip(classes, poids))

    print("   Poids calcules :")
    for code, classe in enumerate(CLASSES):
        print(f"   {classe:20} : {poids_dict[code]:.3f}")

    return poids_dict


def creer_generateurs():
    """
    Générateurs avec augmentation forte pour FROSTYPOD.

    Augmentation train :
    - rotation 30°          -> angles de prise de vue terrain
    - zoom 25%              -> distances variables
    - flip horizontal/verti -> orientation cabosse
    - luminosite [0.6-1.4]  -> ombre / plein soleil CI
    - shear 15°             -> déformation légère
    Source : bonnes pratiques Transfer Learning TensorFlow
    """
    generateur_train = ImageDataGenerator(
        rescale            = 1./255,
        rotation_range     = 30,
        zoom_range         = 0.25,
        horizontal_flip    = True,
        vertical_flip      = True,
        brightness_range   = [0.6, 1.4],
        width_shift_range  = 0.15,
        height_shift_range = 0.15,
        shear_range        = 15,
        fill_mode          = "nearest"
    )

    generateur_valide = ImageDataGenerator(rescale=1./255)
    generateur_test   = ImageDataGenerator(rescale=1./255)

    train_data = generateur_train.flow_from_directory(
        os.path.join(DOSSIER_DATASET, "train"),
        target_size = (IMG_SIZE, IMG_SIZE),
        batch_size  = BATCH_SIZE,
        class_mode  = "categorical",
        classes     = CLASSES,
        shuffle     = True
    )

    valid_data = generateur_valide.flow_from_directory(
        os.path.join(DOSSIER_DATASET, "valid"),
        target_size = (IMG_SIZE, IMG_SIZE),
        batch_size  = BATCH_SIZE,
        class_mode  = "categorical",
        classes     = CLASSES,
        shuffle     = False
    )

    test_data = generateur_test.flow_from_directory(
        os.path.join(DOSSIER_DATASET, "test"),
        target_size = (IMG_SIZE, IMG_SIZE),
        batch_size  = BATCH_SIZE,
        class_mode  = "categorical",
        classes     = CLASSES,
        shuffle     = False
    )

    return train_data, valid_data, test_data


def construire_modele(nb_classes):
    """
    MobileNetV2 avec Transfer Learning.

    Architecture :
    MobileNetV2 (ImageNet) -> GlobalAveragePooling2D
    -> BatchNormalization -> Dense 512 -> Dropout 0.4
    -> Dense 256 -> Dropout 0.3 -> Dense nb_classes softmax

    Ajouts vs v1 :
    - Couche Dense 512 supplementaire
    - Dropout reduit 0.5 -> 0.4 / 0.3
    - BatchNorm apres pooling uniquement

    Source : MobileNetV2 — Sandler et al. 2018
    Precision cible : >85% sur cacao CI (Nyarko 2024)
    """
    print("Construction du modele MobileNetV2 v2...")

    base_model = MobileNetV2(
        input_shape = (IMG_SIZE, IMG_SIZE, 3),
        include_top = False,
        weights     = "imagenet"
    )

    base_model.trainable = False

    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = BatchNormalization()(x)
    x = Dense(512, activation="relu")(x)
    x = Dropout(0.4)(x)
    x = Dense(256, activation="relu")(x)
    x = Dropout(0.3)(x)
    predictions = Dense(nb_classes, activation="softmax")(x)

    modele = Model(inputs=base_model.input, outputs=predictions)

    modele.compile(
        optimizer = Adam(learning_rate=LR),
        loss      = "categorical_crossentropy",
        metrics   = ["accuracy"]
    )

    total    = modele.count_params()
    entraines = sum(
        tf.size(w).numpy() for w in modele.trainable_weights
    )

    print(f"   Parametres totaux    : {total:,}")
    print(f"   Parametres entraines : {entraines:,}")
    print(f"   Classes              : {nb_classes}")

    return modele, base_model


def phase1_entrainement(modele, train_data, valid_data, poids_classes):
    """
    Phase 1 — Entraîne seulement les nouvelles couches.
    Les couches MobileNetV2 restent gelées.
    Plus d'epochs (15 au lieu de 10) + poids classes.
    """
    print("\nPhase 1 — Entrainement couches finales (15 epochs max)...")

    callbacks = [
        EarlyStopping(
            monitor              = "val_accuracy",
            patience             = 6,
            restore_best_weights = True,
            verbose              = 1
        ),
        ReduceLROnPlateau(
            monitor  = "val_loss",
            factor   = 0.5,
            patience = 3,
            min_lr   = 1e-7,
            verbose  = 1
        ),
        ModelCheckpoint(
            filepath       = os.path.join(DOSSIER_MODEL, "best_phase1.keras"),
            monitor        = "val_accuracy",
            save_best_only = True,
            verbose        = 1
        )
    ]

    historique = modele.fit(
        train_data,
        epochs           = 15,
        validation_data  = valid_data,
        callbacks        = callbacks,
        class_weight     = poids_classes,   # CORRECTION DESEQUILIBRE
        verbose          = 1
    )

    return historique


def phase2_finetuning(modele, base_model, train_data, valid_data, poids_classes):
    """
    Phase 2 — Fine-tuning CORRIGE.

    CORRECTIONS vs v1 :
    - Dégèle seulement les 20 dernières couches (vs 30)
    - Learning rate encore plus bas : LR/100 (vs LR/10)
    - Patience augmentee : 8 (vs 7)

    Pourquoi LR/100 ?
    -> LR/10 = 1e-5 detruisait les poids en Phase 2
    -> LR/100 = 1e-6 affine sans casser ce que Phase 1 a appris
    Source : "Practical Deep Learning" — Howard & Gugger 2020
    """
    print("\nPhase 2 — Fine-tuning CORRIGE (20 dernieres couches)...")
    print("   Learning rate : LR/100 = 1e-6")

    # Dégèle seulement les 20 dernières (vs 30 avant)
    base_model.trainable = True
    for layer in base_model.layers[:-20]:
        layer.trainable = False

    couches_entrainables = sum(
        1 for l in base_model.layers if l.trainable
    )
    print(f"   Couches degelees : {couches_entrainables}")

    modele.compile(
        optimizer = Adam(learning_rate=LR / 100),  # LR/100 au lieu de LR/10
        loss      = "categorical_crossentropy",
        metrics   = ["accuracy"]
    )

    callbacks = [
        EarlyStopping(
            monitor              = "val_accuracy",
            patience             = 8,
            restore_best_weights = True,
            verbose              = 1
        ),
        ReduceLROnPlateau(
            monitor  = "val_loss",
            factor   = 0.3,
            patience = 4,
            min_lr   = 1e-8,
            verbose  = 1
        ),
        ModelCheckpoint(
            filepath       = os.path.join(DOSSIER_MODEL, "best_phase2.keras"),
            monitor        = "val_accuracy",
            save_best_only = True,
            verbose        = 1
        )
    ]

    historique = modele.fit(
        train_data,
        epochs          = EPOCHS,
        validation_data = valid_data,
        callbacks       = callbacks,
        class_weight    = poids_classes,
        verbose         = 1
    )

    return historique


def evaluer_modele(modele, test_data):
    """
    Évalue le modèle final sur les données de test.
    """
    print("\nEvaluation sur donnees de test...")

    loss, accuracy = modele.evaluate(test_data, verbose=0)

    print(f"   Loss     : {loss:.4f}")
    print(f"   Accuracy : {accuracy*100:.2f}%")

    predictions  = modele.predict(test_data, verbose=0)
    pred_classes = np.argmax(predictions, axis=1)
    vrai_classes = test_data.classes

    print(f"\nRepartition des predictions :")
    for i, classe in enumerate(CLASSES):
        correct = np.sum((pred_classes == i) & (vrai_classes == i))
        total   = np.sum(vrai_classes == i)
        if total > 0:
            print(f"   {classe:20} : {correct}/{total} "
                  f"({correct/total*100:.1f}% correct)")

    return accuracy


def sauvegarder_modele(modele):
    """
    Sauvegarde en format Keras natif (.keras) et legacy (.h5)
    """
    os.makedirs(DOSSIER_MODEL, exist_ok=True)

    # Format natif Keras (recommande TF 2.x)
    chemin_keras = os.path.join(DOSSIER_MODEL, "modele_maladie.keras")
    modele.save(chemin_keras)
    print(f"Modele sauvegarde : {chemin_keras}")

    # Format legacy .h5 pour compatibilite API Flask
    chemin_h5 = os.path.join(DOSSIER_MODEL, "modele_maladie.h5")
    modele.save(chemin_h5)
    print(f"Modele legacy     : {chemin_h5}")

    classes_path = os.path.join(DOSSIER_MODEL, "classes_maladie.txt")
    with open(classes_path, "w") as f:
        for classe in CLASSES:
            f.write(classe + "\n")
    print(f"Classes sauvegardees : {classes_path}")


def afficher_historique(h1, h2):
    acc1  = h1.history["accuracy"]
    vacc1 = h1.history["val_accuracy"]
    acc2  = h2.history["accuracy"]
    vacc2 = h2.history["val_accuracy"]

    epochs1 = range(1, len(acc1) + 1)
    epochs2 = range(len(acc1) + 1, len(acc1) + len(acc2) + 1)

    plt.figure(figsize=(12, 4))

    plt.subplot(1, 2, 1)
    plt.plot(epochs1, acc1,  "b-",  label="Train Phase 1")
    plt.plot(epochs1, vacc1, "b--", label="Valid Phase 1")
    plt.plot(epochs2, acc2,  "r-",  label="Train Phase 2")
    plt.plot(epochs2, vacc2, "r--", label="Valid Phase 2")
    plt.title("Accuracy par epoch")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.legend()
    plt.grid(True)

    plt.subplot(1, 2, 2)
    loss1  = h1.history["loss"]
    vloss1 = h1.history["val_loss"]
    loss2  = h2.history["loss"]
    vloss2 = h2.history["val_loss"]

    plt.plot(epochs1, loss1,  "b-",  label="Train Phase 1")
    plt.plot(epochs1, vloss1, "b--", label="Valid Phase 1")
    plt.plot(epochs2, loss2,  "r-",  label="Train Phase 2")
    plt.plot(epochs2, vloss2, "r--", label="Valid Phase 2")
    plt.title("Loss par epoch")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig("detection/courbes_apprentissage.png")
    print("Courbes : detection/courbes_apprentissage.png")


# -- PROGRAMME PRINCIPAL --------------------------------------
if __name__ == "__main__":

    print("=" * 55)
    print("   MODELE DETECTION MALADIES CACAO v2")
    print("   MobileNetV2 + Transfer Learning CORRIGE")
    print("=" * 55)
    print(f"   TensorFlow : {tf.__version__}")
    print(f"   GPU         : "
          f"{len(tf.config.list_physical_devices('GPU')) > 0}")
    print("=" * 55)

    fusionner_classes()

    train_data, valid_data, test_data = creer_generateurs()

    print(f"\nDataset :")
    print(f"   Train : {train_data.samples} images")
    print(f"   Valid : {valid_data.samples} images")
    print(f"   Test  : {test_data.samples} images")

    # Poids classes pour corriger le déséquilibre FROSTYPOD
    poids_classes = calculer_poids_classes(train_data)

    modele, base_model = construire_modele(len(CLASSES))

    historique1 = phase1_entrainement(
        modele, train_data, valid_data, poids_classes
    )

    historique2 = phase2_finetuning(
        modele, base_model, train_data, valid_data, poids_classes
    )

    accuracy = evaluer_modele(modele, test_data)

    sauvegarder_modele(modele)

    afficher_historique(historique1, historique2)

    print("\n" + "=" * 55)
    print(f"   TERMINE — Accuracy finale : {accuracy*100:.2f}%")
    print(f"   Cible : > 85%")
    if accuracy >= 0.85:
        print("   Objectif atteint !")
    else:
        print("   Continuer l'optimisation si necessaire")
    print("=" * 55)
