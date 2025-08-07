import json
import time
import random
import os  # NEU: Importiert, um Umgebungsvariablen zu lesen
from datetime import datetime, timezone
from kafka import KafkaProducer  # EINGESCHALTET: Import für den Kafka Producer

# --- Konfiguration ---
ANLAGEN_IDS = ["WKA-01", "WKA-02", "WKA-03", "WKA-04", "WKA-05", "WKA-06"]
ANOMALIE_RATE = 0.05
DATEN_PRO_SEKUNDE = 2

# --- Kafka Konfiguration (JETZT AKTIV) ---
# Holt die Broker-Adresse aus der Umgebungsvariable (die wir in Kubernetes setzen)
# mit einem lokalen Fallback, falls die Variable nicht existiert.
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9094")
KAFKA_TOPIC = "sensor-data"

# --- Kafka Producer Initialisierung (JETZT AKTIV) ---
print(f"Versuche, eine Verbindung zu Kafka herzustellen: {KAFKA_BROKER}")
try:
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        # Serializer wandeln deine Daten in das für Kafka nötige Byte-Format um.
        # Key wird als String -> Bytes kodiert.
        key_serializer=lambda k: k.encode("utf-8"),
        # Value (dict) wird als JSON-String -> Bytes kodiert.
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
    print("Verbindung zu Kafka erfolgreich hergestellt.")
except Exception as e:
    print(f"Fehler bei der Verbindung zu Kafka: {e}")
    producer = None


def generate_normal_data(anlage_id: str) -> dict:
    """Erzeugt einen plausiblen, 'gesunden' Sensordatenpunkt."""
    wind = random.uniform(0, 100)
    rpm = min((wind / 5) + random.uniform(-0.5, 0.5), 20.0)
    if wind < 10:
        rpm = 0
    leistung = min((rpm**3) * 0.05 + random.uniform(-10, 10), 2500.0)
    if rpm == 0:
        leistung = 0
    temp = 40.0 + (leistung / 100) + random.uniform(-2, 2)
    vibration = 0.2 + (rpm / 20) + random.uniform(-0.1, 0.1)
    return {
        "anlage_id": anlage_id,
        "windgeschwindigkeit_kmh": round(wind, 2),
        "rotation_rpm": round(rpm, 2),
        "leistung_kw": round(leistung, 2),
        "getriebe_temp_c": round(temp, 2),
        "vibration_ms2": round(vibration, 2),
        "anomaly": "False",
    }


# (Die generate_..._anomaly Funktionen bleiben exakt gleich)
def generate_overheating_anomaly(anlage_id: str) -> dict:
    data = generate_normal_data(anlage_id)
    data["getriebe_temp_c"] = 95.0 + random.uniform(0, 5)
    data["anomaly"] = "True"
    data["anomaly_type"] = "Overheating"
    return data


def generate_vibration_anomaly(anlage_id: str) -> dict:
    data = generate_normal_data(anlage_id)
    data["vibration_ms2"] = 4.5 + random.uniform(0, 1)
    data["anomaly"] = "True"
    data["anomaly_type"] = "Vibration"
    return data


def generate_icing_anomaly(anlage_id: str) -> dict:
    data = generate_normal_data(anlage_id)
    if data["leistung_kw"] > 500:
        data["leistung_kw"] *= 0.2
        data["anomaly"] = "True"
        data["anomaly_type"] = "Icing"
    return data


def generate_sensor_failure_anomaly(anlage_id: str) -> dict:
    data = generate_normal_data(anlage_id)
    sensor_to_fail = random.choice(["getriebe_temp_c", "rotation_rpm", "vibration_ms2"])
    data[sensor_to_fail] = -999.0
    data["anomaly"] = "True"
    data["anomaly_type"] = "Sensor Failure"
    return data


anomaly_functions = [
    generate_overheating_anomaly,
    generate_vibration_anomaly,
    generate_icing_anomaly,
    generate_sensor_failure_anomaly,
]

# --- Haupt-Schleife des Producers ---
if not producer:
    print("Producer konnte nicht initialisiert werden. Programm wird beendet.")
    exit()

print(f"Starte Producer... Sende Daten an Kafka Topic '{KAFKA_TOPIC}'.")
print("Drücke STRG+C zum Beenden.")

while True:
    try:
        anlage = random.choice(ANLAGEN_IDS)
        if random.random() < ANOMALIE_RATE:
            anomaly_func = random.choice(anomaly_functions)
            final_data = anomaly_func(anlage)
        else:
            final_data = generate_normal_data(anlage)

        final_data["timestamp"] = datetime.now(timezone.utc).isoformat(
            timespec="milliseconds"
        )

        # --- Sendelogik umgestellt ---
        # 1. Lokale Ausgabe ist jetzt auskommentiert
        # print(json.dumps(final_data))

        # 2. Senden an Kafka ist jetzt AKTIV
        producer.send(
            topic=KAFKA_TOPIC,
            key=anlage,  # Der Key sorgt dafür, dass Daten derselben Anlage in derselben Partition landen
            value=final_data,
        )
        print(
            f"Nachricht für {anlage} an Kafka gesendet. Typ: {final_data.get('anomaly_type', 'Normal')}"
        )

        time.sleep(1 / DATEN_PRO_SEKUNDE)

    except KeyboardInterrupt:
        print("\nProducer wird beendet.")
        break
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
        time.sleep(5)

# Producer am Ende schließen
producer.flush()
producer.close()
