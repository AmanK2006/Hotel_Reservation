# Use official lightweight Python 3.12 image
FROM python:3.12-slim

# Prevent Python from writing bytecode files & ensure unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system C++ runtime libraries (libgomp1 for ML models) & cleanup cache
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency resolution
RUN pip install --no-cache-dir uv

# Copy setup files AND requirements.txt to leverage Docker layer caching
COPY pyproject.toml setup.py uv.lock requirements.txt* ./

# Install project dependencies in system scope using uv
RUN uv pip install --system --no-cache -e .

# Copy remaining application & pipeline code
COPY . .

# Run the training pipeline during build stage to generate model artifacts
RUN python pipelines/training_pipeline.py

EXPOSE 5000

# Launch Flask application
CMD ["python", "application.py"]