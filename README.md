Verstanden, hier ist die vollständige Anleitung, die für **Ubuntu** (und andere Debian-basierte Linux-Distributionen) angepasst ist.

-----

### Phase 0: Lokale Multi-Node-Infrastruktur einrichten

Du schaffst die Grundlage: einen lokalen Kubernetes-Cluster auf deinem Ubuntu-Rechner.

#### VORHER INSTALLIEREN

  * **Wo?** Im Terminal deines Ubuntu-Rechners.
  * **Was?**
    1.  **Docker Engine**:
        ```bash
        # Alte Versionen deinstallieren
        sudo apt-get remove docker docker-engine docker.io containerd runc
        # Repository einrichten
        sudo apt-get update
        sudo apt-get install -y ca-certificates curl
        sudo install -m 0755 -d /etc/apt/keyrings
        sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
        sudo chmod a+r /etc/apt/keyrings/docker.asc
        echo \
          "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
          $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
          sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        # Docker Engine installieren
        sudo apt-get update
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        ```
    2.  **Docker ohne `sudo` einrichten (WICHTIG):**
        ```bash
        sudo groupadd docker
        sudo usermod -aG docker $USER
        # WICHTIG: Du musst dich jetzt aus- und wieder einloggen oder 'newgrp docker' ausführen,
        # damit die Gruppenmitgliedschaft wirksam wird.
        ```
    3.  **k3d**: Der Befehl aus der vorherigen Anleitung ist bereits für Linux korrekt.
        ```bash
        curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash
        ```
    4.  **kubectl**:
        ```bash
        curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
        sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
        ```

#### PROZEDUR

1.  **Wo?** Im Terminal deines Ubuntu-Rechners.
2.  **Was?** Erstelle den Multi-Node-Cluster. Der Befehl ist identisch.
    ```bash
    k3d cluster create bigdata-cluster --agents 2 --port '8081:80@loadbalancer'
    ```
3.  **Verifizieren**:
    ```bash
    kubectl get nodes
    ```

-----

### Phase 1: Kafka-Cluster bereitstellen

Jetzt bringst du Kafka, dein Daten-Ingestion-System, in den Kubernetes-Cluster.

#### VORHER INSTALLIEREN

  * **Wo?** Auf deinem Ubuntu-Rechner.
  * **Was?**
    1.  **Helm**: Der Installationsbefehl ist für Linux korrekt.
        ```bash
        curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
        chmod 700 get_helm.sh
        ./get_helm.sh
        ```

#### PROZEDUR

1.  **Wo?** Im Terminal deines Ubuntu-Rechners.
2.  **Was?** Die Prozedur ist identisch zur vorherigen Anleitung.
      * **Strimzi-Repository hinzufügen & Operator installieren**:
        ```bash
        helm repo add strimzi http://strimzi.io/charts/
        helm repo update
        helm install my-kafka-operator strimzi/strimzi-kafka-operator --namespace default
        ```
      * **Kafka-Cluster und Topic definieren**: Erstelle die beiden YAML-Dateien (`kafka-cluster.yaml`, `kafka-topic.yaml`) lokal auf deinem Rechner. Der Inhalt ist derselbe.
      * **Konfigurationen anwenden**:
        ```bash
        kubectl apply -f ./kafka-cluster.yaml
        kubectl apply -f ./kafka-topic.yaml
        ```
3.  **Verifizieren**:
    ```bash
    kubectl get pods -l strimzi.io/cluster=my-kafka-cluster
    ```

-----

### Phase 2: Producer-Anwendung entwickeln & bereitstellen

Das Vorgehen ist für Ubuntu identisch, da alles innerhalb von Docker und Kubernetes abläuft.

#### VORHER INSTALLIEREN

  * **Wo?** Auf deinem Ubuntu-Rechner.
  * **Was?** Python und Pip, falls nicht bereits vorhanden.
    ```bash
    sudo apt-get update
    sudo apt-get install -y python3-pip
    ```

#### PROZEDUR

1.  **Entwicklung (Lokal)**: Erstelle dein Python-Producer-Projekt (Skript, `requirements.txt`, `Dockerfile`, `producer-deployment.yaml`).
2.  **Deployment (Terminal)**: Führe die Befehle aus dem Projektordner aus.
    ```bash
    # Docker-Image bauen
    docker build -t dein-dockerhub-name/sensor-producer:latest .
    # Image hochladen
    docker push dein-dockerhub-name/sensor-producer:latest
    # Producer in K8s starten
    kubectl apply -f ./producer-deployment.yaml
    ```

-----

### Phase 3: Spark-Streaming-Anwendung entwickeln & ausführen

Die Installation von Spark ist unter Linux einfacher als unter Windows.

#### VORHER INSTALLIEREN

  * **Wo?** Auf deinem Ubuntu-Rechner.
  * **Was?**
    1.  **Java Development Kit (JDK)**: Spark benötigt Java.
        ```bash
        sudo apt-get update
        sudo apt-get install -y default-jdk
        ```
    2.  **Apache Spark**:
          * Lade eine Spark-Distribution von der [offiziellen Webseite](https://spark.apache.org/downloads.html) herunter (z.B. Spark 3.5.1).
          * Entpacke die Datei im Terminal:
            ```bash
            # Navigiere zu deinem Download-Ordner
            cd ~/Downloads
            # Entpacke die Datei (passe den Dateinamen an)
            tar xvf spark-3.5.1-bin-hadoop3.tgz
            # Verschiebe den Ordner an einen besseren Ort
            sudo mv spark-3.5.1-bin-hadoop3 /opt/spark
            ```
          * **Umgebungsvariablen setzen**: Öffne deine Shell-Konfigurationsdatei (`~/.bashrc` oder `~/.zshrc`) mit einem Texteditor (z.B. `nano ~/.bashrc`) und füge am Ende diese Zeilen hinzu:
            ```bash
            export SPARK_HOME=/opt/spark
            export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
            ```
          * Lade die Konfiguration neu: `source ~/.bashrc`

#### PROZEDUR

1.  **Entwicklung (Lokal)**: Erstelle dein PySpark-Projekt und die zugehörige `Dockerfile`.
2.  **Deployment (Terminal)**:
      * **Docker-Image bauen und hochladen**:
        ```bash
        docker build -t dein-dockerhub-name/spark-sensor-app:latest .
        docker push dein-dockerhub-name/spark-sensor-app:latest
        ```
      * **Spark-Job an Kubernetes übermitteln**: Der Befehl ist identisch.
        ```bash
        spark-submit \
          --master k8s://https://k3d-bigdata-cluster-server-0:6443 \
          --deploy-mode cluster \
          --name sensor-anomaly-detector \
          --conf spark.executor.instances=2 \
          --conf spark.kubernetes.container.image=dein-dockerhub-name/spark-sensor-app:latest \
          --conf spark.kubernetes.authenticate.driver.serviceAccountName=default \
          local:///opt/spark/work-dir/streaming_app.py
        ```
3.  **Verifizieren**: Die `kubectl`-Befehle zum Prüfen der Pods und Logs sind wieder die gleichen.