from pysiaalarm import SIAClient, SIAAccount
import paho.mqtt.client as mqtt
import os
import time
import json
import re
import logging
import pytz
import unicodedata
import threading

# === CONFIG LOGGING ===
logging.basicConfig(
    filename='/app/logs/sia.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# === CODE SIA TRADUCTION ===
SIA_CODES = {
    "RP": "Désactivé (Disarmed)",
    "CL": "Activation totale (Arm)",
    "NL": "Mode Nuit",
    "OP": "Désactivé (Disarmed)",
    "TA": "Ping (Test automatique)",
    "TR": "Test rétabli",
    "YG": "Sabotage",
    "MA": "Alimentation secteur coupée",
    "WA": "Batterie faible",
    "BA": "Alarm Triggered!"
}
TECH_CODES = ("RP", "TA", "TR")

def remove_accents(text):
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')

# === MQTT SETUP ===
mqtt_client = mqtt.Client(client_id="sia-client")
mqtt_client.will_set("sia/status", payload="offline", qos=1, retain=True)

mqtt_client.username_pw_set(os.getenv("MQTT_USERNAME"), os.getenv("MQTT_PASSWORD"))

def on_disconnect(client, userdata, rc):
    if rc != 0:
        logging.warning(f"⚠️ MQTT déconnecté (code {rc})")
    else:
        logging.info("🛑 Déconnecté proprement du broker MQTT")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("✅ Connexion MQTT établie")
    else:
        logging.error(f"❌ Échec de la connexion MQTT (code {rc})")

mqtt_client.on_disconnect = on_disconnect
mqtt_client.on_connect = on_connect
mqtt_client.reconnect_delay_set(min_delay=5, max_delay=60)

mqtt_client.connect(
    os.getenv("MQTT_HOST"),
    int(os.getenv("MQTT_PORT", 1883)),
    keepalive=30
)
mqtt_client.loop_start()

# === SIA EVENT HANDLER ===
def handle_event(event):
    try:
        logging.debug(f"📥 Événement SIA brut : {event.content}")
        content = event.content

        match = re.search(r'Nri(\d+)/([A-Z]{2})(\d*)\]', content)
        if match:
            zone = int(match.group(1))
            code = match.group(2)
            message = match.group(3)
        else:
            zone = None
            code = "UNKNOWN"
            message = ""

        translated = SIA_CODES.get(code, "Code inconnu")

        if code in TECH_CODES:
            event_type = None
            tech_event = translated
        else:
            event_type = translated
            tech_event = None
        if code == "BA":
            alarm_triggered = True
        else:
            alarm_triggered = False

        data = {
            "account": event.account,
            "timestamp": event.timestamp.astimezone(pytz.timezone("Europe/Paris")).isoformat(),
            "code": code,
            "zone": zone,
            "message": message,
            "event_type": event_type,
            "tech_event": tech_event,
            "alarm_triggered" : alarm_triggered,
            "raw": str(event)
        }

        if event_type:
            mqtt_client.publish("sia/events", json.dumps(data))
            logging.info(f"📤 Événement MQTT publié : {data}")
        else:
            logging.info(f"🔁 Événement technique ignoré pour MQTT : {data}")

    except Exception as e:
        logging.error(f"💥 Exception dans handle_event : {e}")

# === SIA CLIENT SETUP ===
account = SIAAccount(account_id=os.getenv("SIA_ACCOUNT"), key=os.getenv("SIA_PASSWORD"))
client = SIAClient(
    host="0.0.0.0",
    port=int(os.getenv("SIA_PORT", 3000)),
    accounts=[account],
    function=handle_event
)

client.start()
logging.info("🚀 SIA client started and listening...")


def mqtt_keepalive_loop():
    while True:
        mqtt_client.loop()
        mqtt_client.publish("sia/status", "online", qos=1, retain=True)
        logging.info("📶 MQTT ping + online published")
        time.sleep(25)

threading.Thread(target=mqtt_keepalive_loop, daemon=True).start()

try:
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    print("Arrêt manuel.")
