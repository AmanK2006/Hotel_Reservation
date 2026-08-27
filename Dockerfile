# Use official lightweight Python 3.12 image
FROM python:3.12-slim

# Prevent Python from writing bytecode files & ensure unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency configuration files
COPY pyproject.toml setup.py uv.lock requirements.txt* ./

# Install project dependencies
RUN uv pip install --system --no-cache -e .

# Copy remaining project source code
COPY . .

# Accept build argument for GCP service account key
ARG GCP_KEY
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/gcp-key.json

# Authenticate GCP dynamically, run training, and remove key artifact
RUN echo "$GCP_KEY" > /app/gcp-key.json && \
    python pipelines/training_pipeline.py && \
    rm -f /app/gcp-key.json

# Reset credential path env variable for runtime
ENV GOOGLE_APPLICATION_CREDENTIALS=""

EXPOSE 5000

CMD ["python", "application.py"]