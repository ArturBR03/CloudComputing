# CloudComputing

Absolut. Hier ist der detaillierte Fahrplan inklusive aller notwendigen Installationen und Befehle für jede Phase.

-----

### Phase 0: Lokale Multi-Node-Infrastruktur einrichten

In dieser Phase schaffst du die Grundlage für alles Weitere: einen lokalen Kubernetes-Cluster.

#### VORHER INSTALLIEREN

  * **Wo?** Auf deinem lokalen Rechner (Mac, Windows, oder Linux).
  * **Was?**
    1.  **Docker Desktop**: Dies ist die einfachste Methode, um Docker und eine Container-Laufzeitumgebung zu erhalten. Lade es von der offiziellen Docker-Website herunter und installiere es.
    2.  **k3d**: Ein leichtgewichtiger Wrapper, um k3s (eine minimale Kubernetes-Distribution) in Docker zu betreiben.
        ```bash
        # Installation via Script (Mac/Linux)
        curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash
        ```
    3.  **kubectl**: Das Kommandozeilen-Tool zur Steuerung von Kubernetes. Es wird oft mit Docker Desktop mitgeliefert. Prüfe mit `kubectl version`, ob es installiert ist.

#### PROZEDUR

1.  **Wo?** Im Terminal deines lokalen Rechners.
2.  **Was?** Erstelle den Multi-Node-Cluster. Ein "Agent" ist ein Worker-Knoten.
    ```bash
    k3d cluster create bigdata-cluster --agents 2 --port '8081:80@loadbalancer'
    # Das Port-Mapping ist nützlich für späteren Web-UI-Zugriff
    ```
3.  **Verifizieren**: Prüfe, ob dein Cluster mit einem Master und zwei Workern läuft.
    ```bash
    kubectl get nodes
    # Die Ausgabe sollte 3 Knoten anzeigen (1 Server, 2 Agents).
    ```

-----

### Phase 1: Kafka-Cluster bereitstellen

Jetzt bringst du Kafka, dein Daten-Ingestion-System, in den Kubernetes-Cluster.

#### VORHER INSTALLIEREN

  * **Wo?** Auf deinem lokalen Rechner.
  * **Was?**
    1.  **Helm**: Der Paketmanager für Kubernetes.
        ```bash
        # Installation via Script (Mac/Linux)
        curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
        chmod 700 get_helm.sh
        ./get_helm.sh
        ```

#### PROZEDUR

1.  **Wo?** Im Terminal deines lokalen Rechners.
2.  **Was?**
      * **Strimzi-Repository hinzufügen**:
        ```bash
        helm repo add strimzi http://strimzi.io/charts/
        helm repo update
        ```
      * **Strimzi Kafka Operator installieren**:
        ```bash
        helm install my-kafka-operator strimzi/strimzi-kafka-operator --namespace default
        ```
      * **Kafka-Cluster und Topic definieren**: Erstelle lokal zwei YAML-Dateien.
          * `kafka-cluster.yaml`:
            ```yaml
            apiVersion: kafka.strimzi.io/v1beta2
            kind: Kafka
            metadata:
              name: my-kafka-cluster
            spec:
              kafka:
                version: 3.7.0
                replicas: 3
                listeners:
                  - name: plain
                    port: 9092
                    type: internal
                    tls: false
                storage:
                  type: jbod
                  volumes:
                  - id: 0
                    type: persistent-claim
                    size: 10Gi
                    deleteClaim: false
              zookeeper:
                replicas: 3
                storage:
                  type: persistent-claim
                  size: 10Gi
                  deleteClaim: false
            ```
          * `kafka-topic.yaml`:
            ```yaml
            apiVersion: kafka.strimzi.io/v1beta2
            kind: KafkaTopic
            metadata:
              name: sensor-data
              labels:
                strimzi.io/cluster: my-kafka-cluster
            spec:
              partitions: 4
              replicas: 3
            ```
      * **Konfigurationen anwenden**:
        ```bash
        kubectl apply -f kafka-cluster.yaml
        kubectl apply -f kafka-topic.yaml
        ```
3.  **Verifizieren**: Warte einige Minuten und prüfe dann, ob die Kafka-Pods laufen.
    ```bash
    kubectl get pods -l strimzi.io/cluster=my-kafka-cluster
    # Du solltest 3 Kafka-Broker und 3 Zookeeper-Pods sehen.
    ```

-----

### Phase 2: Producer-Anwendung entwickeln & bereitstellen

Jetzt baust du die Anwendung, die deine simulierten Daten erzeugt und in Kafka einspeist.

#### VORHER INSTALLIEREN

  * **Wo?** Auf deinem lokalen Rechner.
  * **Was?** Eine Entwicklungsumgebung für Python (z.B. VS Code) und Python selbst.

#### PROZEDUR

1.  **Wo?** Lokal in einem neuen Projektordner.
2.  **Was?**
      * Schreibe das Python-Skript `producer.py`.
      * Erstelle eine `requirements.txt` mit den Abhängigkeiten (z.B. `kafka-python`).
      * Erstelle eine `Dockerfile`, um die Anwendung zu containerisieren.
      * Erstelle eine `producer-deployment.yaml`, um sie in Kubernetes auszuführen.
3.  **Wo?** Im Terminal deines lokalen Rechners, im Projektordner.
4.  **Was?**
      * **Docker-Image bauen**:
        ```bash
        docker build -t dein-dockerhub-name/sensor-producer:latest .
        ```
      * **Image hochladen**:
        ```bash
        docker push dein-dockerhub-name/sensor-producer:latest
        ```
      * **Producer starten**:
        ```bash
        kubectl apply -f producer-deployment.yaml
        ```
5.  **Verifizieren**: Prüfe die Logs des Producers.
    ```bash
    kubectl get pods
    # Finde den Namen deines Producer-Pods
    kubectl logs <producer-pod-name> -f
    ```

-----

### Phase 3: Spark-Streaming-Anwendung entwickeln & ausführen

Das Herzstück: die Analyse-Anwendung.

#### VORHER INSTALLIEREN

  * **Wo?** Auf deinem lokalen Rechner.
  * **Was?**
    1.  **Apache Spark**: Lade eine Spark-Distribution von der offiziellen Webseite herunter (z.B. Spark 3.5.1 mit Hadoop 3). Entpacke sie lokal. Du brauchst dies für das `spark-submit`-Tool. Füge das `bin`-Verzeichnis von Spark zu deinem systemweiten `PATH` hinzu.

#### PROZEDUR

1.  **Wo?** Lokal in einem neuen Projektordner.
2.  **Was?**
      * Schreibe dein PySpark-Skript `streaming_app.py`.
      * Erstelle eine `requirements.txt`.
      * Erstelle eine `Dockerfile` (wichtig: nutze ein PySpark-fähiges Basis-Image).
3.  **Wo?** Im Terminal deines lokalen Rechners, im Projektordner.
4.  **Was?**
      * **Docker-Image bauen und hochladen**:
        ```bash
        docker build -t dein-dockerhub-name/spark-sensor-app:latest .
        docker push dein-dockerhub-name/spark-sensor-app:latest
        ```
      * **Spark-Job an Kubernetes übermitteln**: Dies ist der magische Befehl.
        ```bash
        # Führe diesen Befehl aus deinem lokalen Terminal aus!
        spark-submit \
          --master k8s://https://k3d-bigdata-cluster-server-0:6443 \
          --deploy-mode cluster \
          --name sensor-anomaly-detector \
          --conf spark.executor.instances=2 \
          --conf spark.kubernetes.container.image=dein-dockerhub-name/spark-sensor-app:latest \
          --conf spark.kubernetes.authenticate.driver.serviceAccountName=default \
          local:///opt/spark/work-dir/streaming_app.py
        ```
        *Erklärung*: Du sagst `spark-submit`, es soll sich mit deinem lokalen k3d-Cluster verbinden (`--master`), den Job im Cluster-Modus ausführen und für die Worker (`Executors`) dein erstelltes Docker-Image verwenden.
5.  **Verifizieren**: Beobachte, wie Spark die Pods erstellt und die Logs des Drivers.
    ```bash
    kubectl get pods
    # Du solltest einen Driver-Pod und 2 Executor-Pods sehen.
    kubectl logs <spark-driver-pod-name> -f
    # Hier siehst du die Ausgabe deiner Streaming-Analyse.
    ```