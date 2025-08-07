# Schritt 1: Wähle ein Basis-Image
# Wir nehmen ein offizielles, schlankes Python-Image. Das enthält bereits Python und den Paketmanager 'pip'.
FROM python:3.9-slim

# Schritt 2: Lege ein Arbeitsverzeichnis im Container fest
# Alle folgenden Befehle werden in diesem Ordner ausgeführt.
WORKDIR /app

# Schritt 3: Kopiere die Abhängigkeiten und installiere sie
# Wir kopieren zuerst nur die requirements.txt, um den Docker Build-Cache optimal zu nutzen.
COPY requirements.txt .
# Führe pip aus, um die in der Datei aufgelisteten Bibliotheken zu installieren.
RUN pip install --no-cache-dir -r requirements.txt

# Schritt 4: Kopiere dein eigentliches Python-Skript
COPY producer.py .

# Schritt 5: Lege den Befehl fest, der beim Starten des Containers ausgeführt wird
CMD ["python", "producer.py"]
