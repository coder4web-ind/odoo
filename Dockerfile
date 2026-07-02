FROM docker.io/library/python:3.12-slim

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    libldap2-dev \
    libsasl2-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 👇 ADD THIS LINE TO BAKE YOUR CODE INTO THE IMAGE
COPY . .