# Cacao Intelligent : Analyse des Problématiques Terrain et Solutions Apportées

Ce document détaille, de manière transparente et réaliste, la capacité du système **Cacao Intelligent** à résoudre les problèmes majeurs rencontrés par les agriculteurs sur le terrain. Il met en évidence nos solutions techniques, ainsi que les limites assumées de notre prototype (ce qu'il ne peut pas encore faire).

---

## 1. Vulnérabilité Face au Climat
**Le Problème :** Les agriculteurs sont victimes de sécheresses imprévisibles et du décalage des saisons des pluies, rendant les calendriers agricoles traditionnels obsolètes.

✅ **Ce que Cacao Intelligent résout : L'adaptation au microclimat**
*   **La Solution :** Le système ne se base plus sur des probabilités générales, mais sur la réalité locale. Grâce aux capteurs IoT (humidité du sol, température, précipitations) placés sur la parcelle, l'Intelligence Artificielle récolte les données en temps réel.
*   **L'Impact :** L'IA génère des alertes SMS ciblées et au bon moment. Par exemple : *"Sécheresse critique du sol détectée, irriguez dans les 48h"* ou *"Alerte précipitation, repoussez la pulvérisation des intrants"*.

---

## 2. Maladies du Cacao et Contrefaçons de Produits
**Le Problème :** La difficulté d'identifier la maladie exacte (ex: *Moniliophthora roreri* face à la Pourriture Brune) pousse l'agriculteur à utiliser le mauvais traitement, ou pire, à acheter des pesticides frelatés/contrefaits.

✅ **Ce que Cacao Intelligent résout : Le Diagnostic Précis**
*   **La Solution :** Le module d'analyse d'images par IA permet de prendre en photo une cabosse suspecte. L'algorithme classifie l'anomalie et recommande immédiatement la bonne molécule active à appliquer. Le traitement n'est plus aléatoire.

❌ **La Limite Assumée : Les Contrefaçons Chimiques**
*   **Ce que le système ne fait pas :** La V1 de notre application conseille le pesticide idéal, mais ne peut empêcher physiquement l'agriculteur d'acheter un "faux" produit au marché local.
*   **Perspective d'évolution (Future) :** Intégrer une "Marketplace SNOI", un catalogue de fournisseurs d'intrants certifiés directement dans l'application, afin de garantir l'origine des produits.

---

## 3. Gestion des Sols et Choix des Engrais
**Le Problème :** Les agriculteurs connaissent mal la chimie précise de leur parcelle et utilisent des engrais inadaptés.

⚠️ **Ce que Cacao Intelligent résout Partiellement : Optimisation de l'Apport**
*   **La Solution :** Le système optimise le *moment* de la fertilisation grâce à la mesure de l'humidité du sol via IoT (l'engrais nécessite de l'eau pour pénétrer le sol efficacement).
*   **Ce que le système ne fait pas :** À moins d'utiliser des sondes NPK (Azote, Phosphore, Potassium) très coûteuses, le système ne fait pas la chimie du sol.
*   **Perspective d'évolution (Future) :** L'agriculteur devra toujours faire analyser sa terre par un laboratoire, mais les résultats de cette analyse pourront être saisis manuellement dans son profil de l'application pour calibrer plus finement les prédictions de l'IA.

---

## 4. Opacité des Coopératives et Mauvaise Gestion
**Le Problème :** Gestion souvent archaïque (cahiers) entraînant des "pertes" d'informations, du népotisme, ou des falsifications de poids au détriment du petit producteur.

✅ **Ce que Cacao Intelligent résout : La Traçabilité Immuable**
*   **La Solution :** Tout acte est horodaté et sécurisé. Lors de la récolte, l'agriculteur crée numériquement son Lot sous son identité certifiée, ce qui génère un QR Code unique "En Attente".
*   **L'Impact :** La coopérative est contrainte d'accepter le lot dans le système informatique. La validation numérique constitue une preuve irréfutable pour l'agriculteur (poids, date, heure) qui apparaît sur son téléphone. La table d'historique du backend gère même la résolution de "Conflits", supprimant le pouvoir de l'intermédiaire de nier une réception.

---

## 5. Non-Respect du Prix Fixé et Abus des Acheteurs (Pisteurs)
**Le Problème :** Les intermédiaires profitent de la vulnérabilité temporelle ou logistique des agriculteurs pour payer en espèces, en dessous du "Prix Garanti Bord Champ" fixé par le Conseil du Café-Cacao.

✅ **Ce que Cacao Intelligent résout : Numérisation de la Valeur Légale**
*   **La Solution :** En numérisant la récolte dès la parcelle et en la liant à l'Identité Nationale Numérique (SNOI) de l'agriculteur, le lot ne peut transiter vers la coopérative ou l'exportateur qu'après un scan du QR Code qui expose publiquement son volume (ex: 500 kg).
*   **La Garantie Interactive :** Si ce statut logiciel est couplé au paiement via un système comme Mobile Money (ex: Wave), le système agit comme tiers de confiance. Le passage au statut "Collecté" ne peut s'opérer que si la somme correspondante au (Poids × Prix Officiel de l'État) transite bien vers le compte (ID) de l'agriculteur. L'arnaque liée aux arrangements occultes en espèces disparaît.
