from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    FloatType,
    TimestampType,
)

# Kafka-Server-Adresse, die Spark im Kubernetes-Netzwerk verwenden wird
KAFKA_BROKER = "my-kafka-cluster-kafka-bootstrap:9092"
KAFKA_TOPIC = "sensor-data"

# Erstelle eine Spark Session
spark = SparkSession.builder.appName("SensorAnomalyDetector").getOrCreate()

# Definiere das Schema für die eingehenden JSON-Daten
schema = StructType(
    [
        StructField("anlage_id", StringType(), True),
        StructField("timestamp", StringType(), True),
        StructField("windgeschwindigkeit_kmh", FloatType(), True),
        StructField("rotation_rpm", FloatType(), True),
        StructField("leistung_kw", FloatType(), True),
        StructField("getriebe_temp_c", FloatType(), True),
        StructField("vibration_ms2", FloatType(), True),
        StructField("anomaly", StringType(), True),
        StructField("anomaly_type", StringType(), True),
    ]
)

# Erstelle einen Streaming-DataFrame, der vom Kafka-Topic liest
kafka_df = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", KAFKA_BROKER)
    .option("subscribe", KAFKA_TOPIC)
    .load()
)

# Konvertiere die JSON-Daten aus der 'value'-Spalte in strukturierte Daten
parsed_df = (
    kafka_df.selectExpr("CAST(value AS STRING)")
    .select(from_json(col("value"), schema).alias("data"))
    .select("data.*")
    .withColumn("timestamp", col("timestamp").cast(TimestampType()))
)  # Konvertiere String zu echtem Zeitstempel

# Filtere nur die Anomalien
anomalies_df = parsed_df.where("anomaly == 'True'")

# Zähle Anomalien pro Anlagentyp in einem 5-Minuten-Zeitfenster
anomaly_counts = (
    anomalies_df.withWatermark("timestamp", "10 minutes")
    .groupBy(
        window(col("timestamp"), "5 minutes"), col("anlage_id"), col("anomaly_type")
    )
    .count()
)

# Gib den Ergebnis-Stream in der Konsole aus
query = (
    anomaly_counts.writeStream.outputMode("update")
    .format("console")
    .option("truncate", "false")
    .start()
)

query.awaitTermination()
