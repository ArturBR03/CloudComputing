import json
import time
import random
from datetime import datetime, timezone

# from kafka import KafkaProducer # Später für die echte Anbindung aktivieren

# --- Konfiguration ---
ANLAGEN_IDS = ["WKA-01", "WKA-02", "WKA-03", "WKA-04", "WKA-05", "WKA-06"]
ANOMALIE_RATE = 0.05  # 5% der Nachrichten sollen Anomalien sein
DATEN_PRO_SEKUNDE = 2  # Sende 2 Datenpunkte pro Sekunde

# --- Kafka Konfiguration (für später) ---
# KAFKA_BROKER = 'my-kafka-cluster-kafka-bootstrap:9092' # Adresse aus deinem K8s-Cluster
# KAFKA_TOPIC = 'sensor-data'

# try:
#     producer = KafkaProducer(
#         bootstrap_servers=KAFKA_BROKER,
#         value_serializer=lambda v: json.dumps(v).encode('utf-8'),
#         key_serializer=lambda k: k.encode('utf-8')
#     )
# except Exception as e:
#     print(f"Fehler bei der Verbindung zu Kafka: {e}")
#     producer = None


def generate_normal_data(anlage_id: str) -> dict:
    """
    Erzeugt einen plausiblen, "gesunden" Sensordatenpunkt.
    Die Werte sind voneinander abhängig, um ein realistisches Muster zu erzeugen.
    """
    wind = random.uniform(0, 100)

    # Rotation hängt vom Wind ab, ist aber bei max. 20 RPM gedeckelt
    rpm = min((wind / 5) + random.uniform(-0.5, 0.5), 20.0)
    if wind < 10:
        rpm = 0

    # Leistung hängt kubisch von der Rotation ab, max. 2500 kW
    leistung = min((rpm**3) * 0.05 + random.uniform(-10, 10), 2500.0)
    if rpm == 0:
        leistung = 0

    # Temperatur hängt von der Leistung ab
    temp = 40.0 + (leistung / 100) + random.uniform(-2, 2)

    # Vibration hängt von der Rotation ab
    vibration = 0.2 + (rpm / 20) + random.uniform(-0.1, 0.1)

    return {
        "anlage_id": anlage_id,
        "windgeschwindigkeit_kmh": round(wind, 2),
        "rotation_rpm": round(rpm, 2),
        "leistung_kw": round(leistung, 2),
        "getriebe_temp_c": round(temp, 2),
        "vibration_ms2": round(vibration, 2),
        "anomaly": "False",  # Kennzeichnung als normale Daten
    }


def generate_overheating_anomaly(anlage_id: str) -> dict:
    """Simuliert eine Getriebe-Überhitzung."""
    data = generate_normal_data(anlage_id)
    # Temperatur ist unplausibel hoch für die gegebene Leistung
    data["getriebe_temp_c"] = 95.0 + random.uniform(0, 5)
    data["anomaly"] = "True"
    data["anomaly_type"] = "Overheating"
    return data


def generate_vibration_anomaly(anlage_id: str) -> dict:
    """Simuliert extreme Vibrationen."""
    data = generate_normal_data(anlage_id)
    # Vibration ist unplausibel hoch für die gegebene Rotation
    data["vibration_ms2"] = 4.5 + random.uniform(0, 1)
    data["anomaly"] = "True"
    data["anomaly_type"] = "Vibration"
    return data


def generate_icing_anomaly(anlage_id: str) -> dict:
    """Simuliert Leistungsverlust durch Vereisung."""
    data = generate_normal_data(anlage_id)
    # Sorge dafür, dass wir einen Fall mit hoher Leistung haben
    if data["leistung_kw"] > 500:
        # Leistung bricht auf 20% ein, obwohl Wind und RPM hoch sind
        data["leistung_kw"] *= 0.2
        data["anomaly"] = "True"
        data["anomaly_type"] = "Icing"
    return data


def generate_sensor_failure_anomaly(anlage_id: str) -> dict:
    """Simuliert den Ausfall eines Sensors mit unsinnigen Werten."""
    data = generate_normal_data(anlage_id)
    # Wähle zufällig einen Sensor, der ausfällt
    sensor_to_fail = random.choice(["getriebe_temp_c", "rotation_rpm", "vibration_ms2"])
    data[sensor_to_fail] = -999.0
    data["anomaly"] = "True"
    data["anomaly_type"] = "Sensor Failure"
    return data


# --- Haupt-Schleife des Producers ---

# Liste mit den Funktionen, die eine Anomalie erzeugen
anomaly_functions = [
    generate_overheating_anomaly,
    generate_vibration_anomaly,
    generate_icing_anomaly,
    generate_sensor_failure_anomaly,
]

print("Starte Producer... Sende Daten an die Konsole.")
print("Drücke STRG+C zum Beenden.")

while True:
    try:
        anlage = random.choice(ANLAGEN_IDS)

        # Entscheide zufällig, ob eine Anomalie erzeugt wird
        if random.random() < ANOMALIE_RATE:
            # Wähle eine zufällige Anomalie-Art aus der Liste
            anomaly_func = random.choice(anomaly_functions)
            final_data = anomaly_func(anlage)
        else:
            final_data = generate_normal_data(anlage)

        final_data["timestamp"] = datetime.now(timezone.utc).isoformat(
            timespec="milliseconds"
        )

        # --- Hier zwischen lokaler Entwicklung und Kafka umschalten ---

        # 1. Für die lokale Entwicklung: An die Konsole ausgeben
        print(json.dumps(final_data))

        # 2. Für das spätere Deployment in Kubernetes: An Kafka senden
        # if producer:
        #     producer.send(
        #         topic=KAFKA_TOPIC,
        #         key=anlage,
        #         value=final_data
        #     )
        #     print(f"Nachricht an Kafka gesendet für {anlage}")
        # else:
        #     print("Kafka-Producer nicht verbunden, kann nicht senden.")

        time.sleep(1 / DATEN_PRO_SEKUNDE)

    except KeyboardInterrupt:
        print("\nProducer wird beendet.")
        break
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
        time.sleep(5)
