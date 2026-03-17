from twilio.rest import Client
from datetime import datetime


# -- CONFIGURATION --------------------------------------------
# Remplace par tes vraies valeurs Twilio (utiliser des variables d'environnement en production)
import os
from dotenv import load_dotenv

# Charger les variables du fichier .env
load_dotenv()
ACCOUNT_SID         = os.environ.get("TWILIO_ACCOUNT_SID", "AC_VOTRE_SID_ICI")
AUTH_TOKEN          = os.environ.get("TWILIO_AUTH_TOKEN", "VOTRE_TOKEN_ICI")
TWILIO_NUM          = os.environ.get("TWILIO_NUM", "+1234567890")
MESSAGING_SERVICE   = os.environ.get("TWILIO_MESSAGING_SERVICE", "MG_VOTRE_SERVICE_ICI")

# Numéro de l'agriculteur destinataire (ton numéro vérifié)
NUMERO_AGRICULTEUR  = os.environ.get("NUMERO_AGRICULTEUR", "+2250000000000")


# -- CLIENT TWILIO --------------------------------------------
client = Client(ACCOUNT_SID, AUTH_TOKEN)


# -- FONCTIONS SMS --------------------------------------------

def envoyer_sms(message):
    """
    Envoie un SMS via le Messaging Service Twilio.
    Utilise MessagingServiceSid pour la fiabilité.
    Source : Twilio docs — Messaging Service
    """
    try:
        sms = client.messages.create(
            body                = message,
            messaging_service_sid = MESSAGING_SERVICE,
            to                  = NUMERO_AGRICULTEUR
        )
        print(f"SMS envoye : {sms.sid}")
        return True
    except Exception as e:
        print(f"Erreur SMS : {e}")
        return False


def sms_maladie_detectee(maladie, confiance, action, parcelle_gps=None):
    emojis = {"BLACKPOD": "ROUGE", "FROSTYPOD": "ORANGE",
              "MIRID": "VIOLET", "HEALTHY": "OK"}
    heure  = datetime.now().strftime("%d/%m %H:%M")
    msg = (
        f"CACAO {heure}\n"
        f"MALADIE: {maladie} {confiance}%\n"
        f"ACTION: {action}"
    )
    return envoyer_sms(msg)


def sms_irrigation(decision, confiance, humidite_sol, saison):
    heure = datetime.now().strftime("%d/%m %H:%M")
    if decision == 1:
        msg = f"CACAO {heure}\nIRRIGATION OUI\nSol:{humidite_sol}% Conf:{confiance}%"
    else:
        msg = f"CACAO {heure}\nIRRIGATION NON\nSol:{humidite_sol}% Conf:{confiance}%"
    return envoyer_sms(msg)


def sms_pulverisation(decision, confiance, maladie=None, saison=None):
    heure = datetime.now().strftime("%d/%m %H:%M")
    if decision == 1:
        mal = f" {maladie}" if maladie else ""
        msg = f"CACAO {heure}\nPULVERISATION OUI{mal}\nConf:{confiance}%"
    else:
        msg = f"CACAO {heure}\nPULVERISATION NON\nConf:{confiance}%"
    return envoyer_sms(msg)


def sms_frostypod(confiance, parcelle_gps=None):
    heure = datetime.now().strftime("%d/%m %H:%M")
    msg = (
        f"CACAO {heure}\n"
        f"MONILIOSE {confiance}%\n"
        f"RETIRER cabosses urgt\n"
        f"Src:ICCO/FAO"
    )
    return envoyer_sms(msg)


def sms_conflit(message_conflit, heures_restantes=None):
    heure = datetime.now().strftime("%d/%m %H:%M")
    attente = f" Attendre {heures_restantes}h" if heures_restantes else ""
    msg = f"CACAO {heure}\nCONFLIT:{attente}"
    return envoyer_sms(msg)

# -- TEST DIRECT ----------------------------------------------
if __name__ == "__main__":
    print("=" * 45)
    print("   TEST MODULE SMS — CACAO INTELLIGENT")
    print("=" * 45)

    print("\nTest 1 — Maladie BLACKPOD...")
    sms_maladie_detectee(
        maladie     = "BLACKPOD",
        confiance   = 82.7,
        action      = "Pulveriser fongicide dans les 24h",
        parcelle_gps= "5.7833,-6.5833"
    )

    print("Test 2 — Irrigation recommandee...")
    sms_irrigation(
        decision    = 1,
        confiance   = 91.2,
        humidite_sol= 28.0,
        saison      = "Grande saison seche"
    )

    print("Test 3 — FROSTYPOD urgent...")
    sms_frostypod(
        confiance   = 91.4,
        parcelle_gps= "5.7833,-6.5833"
    )

    print("\nTests termines — verifie tes SMS !")
    print("=" * 45)