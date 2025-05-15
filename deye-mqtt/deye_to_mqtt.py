import asyncio
import os
import logging
import json
from datetime import datetime
import paho.mqtt.client as mqtt

from pysolarman import Solarman

registres = {
    "pv1_voltage": (0x006D, 0.1),
    "pv1_current": (0x006E, 0.1),
    "pv2_voltage": (0x006F, 0.1),
    "pv2_current": (0x0070, 0.1),
    "battery_voltage": (0x00B7, 0.01),
    "battery_percent": (0x00B8, 1),
    "battery_power": (0x00BE, 1),
    "grid_power": (0x00A9, 1),
    "load_power": (0x00B2, 1),
    "generator_power": (0x00A6, 1),
    "generator_voltage": (0x00B5, 0.1),
    "generator_frequency": (0x00C4, 0.01),
    "battery_temperature": (0x00B6, 0.1),
    "inverter_dc_temp": (0x005A, 0.1),
    "inverter_temp": (0x005B, 0.1),
}

temperature_keys = {
    "battery_temperature",
    "inverter_dc_temp",
    "inverter_temp",
}

signed_keys = {
    "battery_power",
    "grid_power",
    "load_power",
    "generator_power",
    "pv1_current",
    "pv2_current",
}

log_dir = "/app/logs"
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, "deye.log"),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logging.getLogger().addHandler(logging.StreamHandler())

def safe_temp_offset1000(raw_value, scale=0.1, offset=1000):
    return round((raw_value - offset) * scale, 1)

mqtt_client = mqtt.Client(client_id="deye-mqtt")
mqtt_host = os.getenv("MQTT_BROKER", "localhost")
mqtt_port = int(os.getenv("MQTT_PORT", 1883))
mqtt_user = os.getenv("MQTT_USER")
mqtt_pass = os.getenv("MQTT_PASSWORD")

if mqtt_user:
    mqtt_client.username_pw_set(mqtt_user, mqtt_pass)

def publish_json_mqtt(topic, payload_dict):
    try:
        mqtt_client.publish(topic, payload=json.dumps(payload_dict), qos=0, retain=False)
        logging.info(f"📡 Published {topic} = {payload_dict}")
    except Exception as e:
        logging.error(f"❌ MQTT publish error: {e}")

async def poll_loop():
    client = Solarman(
        address="192.168.10.167",
        port=8899,
        transport="tcp",
        serial=0,
        slave=1,
        timeout=10
    )

    while True:
        await client.open()
        data = {}
        try:
            for key, (reg, scale) in registres.items():
                try:
                    val = await client.execute(0x03, address=reg, count=1)
                    raw = val[0]

                    if key in signed_keys and raw > 32767:
                        raw -= 65536

                    if key in temperature_keys:
                        value = safe_temp_offset1000(raw, scale)
                    else:
                        value = round(raw * scale, 2)

                    data[key] = value
                except Exception as e:
                    logging.warning(f"⚠️ {key}: erreur → {e}")
        finally:
            await client.close()

        publish_json_mqtt("deye/events", data)
        await asyncio.sleep(10)

if __name__ == "__main__":
    mqtt_client.connect(mqtt_host, mqtt_port, keepalive=60)
    mqtt_client.loop_start()
    try:
        asyncio.run(poll_loop())
    except KeyboardInterrupt:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
