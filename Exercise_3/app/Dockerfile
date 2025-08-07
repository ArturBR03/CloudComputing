FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    libgomp1 && \
    rm -rf /var/lib/apt/lists/*

# Copy code
COPY requirements.txt .
COPY World_bank.py .
COPY main.py .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Run preprocessing script before starting app
CMD ["sh", "-c", "python World_bank.py && streamlit run main.py --server.port=8501 --server.address=0.0.0.0"]
