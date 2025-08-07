# Schritt 1: Wähle ein offizielles PySpark-Basis-Image
# Dieses Image enthält bereits eine komplette Spark- und Python-Umgebung.
FROM bitnami/spark:3.5

# Schritt 2: Lege das Arbeitsverzeichnis fest (dies ist der Standard-Pfad für Spark)
WORKDIR /opt/spark/work-dir

# Schritt 3: Kopiere nur dein Spark-Skript hinein
COPY streaming_app.py .
