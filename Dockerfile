# Use official lightweight Python 3.12 image
FROM python:3.12-slim

# Prevent Python from writing bytecode files, ensure unbuffered logging, & set PYTHONPATH
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install system C++ runtime libraries (libgomp1 for ML models) & cleanup cache
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency resolution
RUN pip install --no-cache-dir uv

# Copy dependency setup files
COPY pyproject.toml setup.py uv.lock requirements.txt* ./

# Install project dependencies into system environment
RUN uv pip install --system --no-cache -e .

# Copy application source code
COPY . .

EXPOSE 8080

# Launch Flask application
CMD ["python", "application.py"]