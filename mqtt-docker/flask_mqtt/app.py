from flask import Flask, jsonify
import paho.mqtt.client as mqtt
import json
import os
import logging
from logging.handlers import RotatingFileHandler
import os


MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_USER = os.getenv("MQTT_USER", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")
MQTT_TOPIC = "#"

data_store = {}

app = Flask(__name__)


app = Flask(__name__)

# === LOGGING SETUP ===
if not os.path.exists('logs'):
    os.makedirs('logs')

file_handler = RotatingFileHandler('logs/flask_app.log', maxBytes=10240, backupCount=3)
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
)
file_handler.setFormatter(formatter)

app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Flask app startup')

# Werkzeug (access logs)
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.INFO)
werkzeug_logger.addHandler(file_handler)


# === MQTT Setup ===
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        app.logger.info("✅ Connected to MQTT broker")
        client.subscribe(MQTT_TOPIC)
    else:
        app.logger.error(f"❌ Failed to connect. Code: {rc}")

def on_message(client, userdata, msg):
    log_msg = f"📥 Received: {msg.topic} => {msg.payload}"
    app.logger.info(log_msg)
    try:
        payload_str = msg.payload.decode("utf-8").strip()
        if not payload_str or not payload_str.startswith(('{', '[')):
            app.logger.warning(f"⛔ Ignored non-JSON message on topic {msg.topic}")
            return

        payload = json.loads(payload_str)
        data_store[msg.topic] = payload
    except Exception as e:
        app.logger.error(f"⚠️ Error parsing message: {e}")


def on_message(client, userdata, msg):
    print(f"📥 Received: {msg.topic} => {msg.payload}")
    try:
        payload_str = msg.payload.decode("utf-8").strip()
        if not payload_str or not payload_str.startswith(('{', '[')):
            print(f"⛔ Ignored non-JSON message on topic {msg.topic}")
            return

        payload = json.loads(payload_str)
        data_store[msg.topic] = payload
    except Exception as e:
        print(f"⚠️ Error parsing message: {e}")


client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

# === API Routes ===

@app.route('/api/data', methods=['GET'])
def get_all_data():
    return jsonify(data_store)

@app.route('/api/data/<path:topic>', methods=['GET'])
def get_topic_data(topic):
    full_topic = f"{MQTT_TOPIC.split('#')[0]}{topic}"
    if full_topic in data_store:
        return jsonify({full_topic: data_store[full_topic]})

    results = {}
    for t, payload in data_store.items():
        if isinstance(payload, dict) and topic in payload:
            results[t] = payload[topic]

    if results:
        return jsonify(results)

    return jsonify({"error": "Topic or key not found"}), 404

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True, port=8080, use_reloader=False)
