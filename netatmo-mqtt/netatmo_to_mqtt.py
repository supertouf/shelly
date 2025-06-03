import os
import time
import json
import requests
import logging
import paho.mqtt.client as mqtt
from time import time as now
import sys

# === LOGGING ===
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

logging.info("🚀 Démarrage du script Netatmo -> MQTT")

# === MQTT CONFIG ===
MQTT_HOST = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_USER = os.getenv("MQTT_USER", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")
MQTT_TOPIC = "netatmo/events"

# === NETATMO CONFIG ===
CLIENT_ID = os.environ["NETATMO_CLIENT_ID"]
CLIENT_SECRET = os.environ["NETATMO_CLIENT_SECRET"]
TOKENS_FILE = "tokens.json"
POLL_INTERVAL = int(os.getenv("NETATMO_POLL_INTERVAL", 15))  # secondes

# === MQTT Client Setup ===
client = mqtt.Client(client_id="netatmo-client")
if MQTT_USER:
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("✅ Connecté au broker MQTT")
    else:
        logging.error(f"❌ Erreur de connexion MQTT, code: {rc}")

def on_disconnect(client, userdata, rc):
    logging.info("⚠️ Déconnecté du broker MQTT")

client.on_connect = on_connect
client.on_disconnect = on_disconnect

# === Token helpers ===
def load_tokens():
    try:
        with open(TOKENS_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"❌ Impossible de charger le fichier tokens : {e}")
        return {}

def save_tokens(new_tokens):
    current = load_tokens()
    expires_in = new_tokens.get("expires_in", 10800)  # défaut : 3h
    merged = {
        "access_token": new_tokens.get("access_token", current.get("access_token")),
        "refresh_token": new_tokens.get("refresh_token", current.get("refresh_token")),
        "expires_at": int(now()) + expires_in
    }
    with open(TOKENS_FILE, "w") as f:
        json.dump(merged, f)

def get_valid_access_token():
    tokens = load_tokens()
    expires_at = tokens.get("expires_at")
    access_token = tokens.get("access_token")

    if not access_token or not expires_at or now() >= expires_at:
        logging.info("🔁 access_token expiré ou manquant, rafraîchissement...")
        refresh_token = tokens.get("refresh_token")
        if not refresh_token:
            raise Exception("❌ Aucun refresh_token trouvé.")
        url = "https://api.netatmo.com/oauth2/token"
        data = {
            "grant_type": "refresh_token",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": refresh_token,
        }
        response = requests.post(url, data=data)
        if response.status_code == 403:
            logging.warning("⛔ Appel Netatmo rejeté (403) – peut-être trop fréquent ?")
        response.raise_for_status()
        tokens = response.json()
        logging.info("🔐 Token Netatmo rafraîchi")
        save_tokens(tokens)
        return tokens["access_token"]
    else:
        minutes_remaining = int((expires_at - now()) / 60)
        logging.info(f"🔒 access_token encore valide pendant {minutes_remaining} min")
        return access_token


# === Récupération des données météo ===
def get_weather_data(access_token):
    url = "https://api.netatmo.com/api/getstationsdata"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 403:
        logging.warning("⛔ Appel Netatmo rejeté (403) – peut-être trop fréquent ?")
    response.raise_for_status()
    return response.json()

# === Boucle principale ===
if __name__ == "__main__":
    try:
        while True:
            try:
                token = get_valid_access_token()
                weather = get_weather_data(token)

                logging.info("📦 Données météo récupérées : "+json.dumps(weather))

                client.connect(MQTT_HOST, MQTT_PORT, 60)
                client.loop_start()
                time.sleep(1)

                result = client.publish(MQTT_TOPIC, json.dumps(weather), qos=0, retain=False)

                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    logging.info(f"📤 Données publiées sur topic {MQTT_TOPIC}")
                else:
                    logging.error(f"❌ Échec publication MQTT : {result.rc}")

                client.loop_stop()
                client.disconnect()

            except Exception as e:
                logging.exception(f"❗ Erreur dans la boucle : {e}")

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        logging.info("⛔ Arrêt manuel")
    except Exception as e:
        logging.exception(f"❗ Erreur fatale : {e}")
