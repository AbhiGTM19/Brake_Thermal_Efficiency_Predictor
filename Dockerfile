# --- Stage 1: Builder ---
FROM python:3.14-slim as builder

WORKDIR /app

# Install build tools if necessary
RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- Stage 2: Final Image ---
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Hugging Face Spaces specifically requires the app to run as user 1000
RUN useradd -m -u 1000 appuser

WORKDIR /home/appuser/app

# Copy dependencies
COPY --from=builder /usr/local/lib/python3.14/site-packages/ /usr/local/lib/python3.14/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy application files and change ownership
COPY --chown=1000:1000 . .

# Ensure mlruns directory exists and is writable by appuser
RUN mkdir -p /home/appuser/app/mlruns && chown -R 1000:1000 /home/appuser/app/mlruns

# Switch to non-root user
USER 1000

# Run training to generate local MLflow artifacts with correct container absolute paths
RUN rm -rf /home/appuser/app/mlruns && python train.py

# Expose port 7860 for Hugging Face
EXPOSE 7860

# Run Uvicorn with port 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860", "--proxy-headers", "--forwarded-allow-ips", "*"]