FROM docker.io/library/python:3.12-slim

# Install system C headers needed for Odoo 19 database and layout compilation
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    libldap2-dev \
    libsasl2-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Copy and pre-install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt