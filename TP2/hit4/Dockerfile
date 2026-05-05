# Stage 1: Build dependencies
FROM python:3.12.10-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt
# Nota: psycopg2-binary trae sus propias librerías de cliente Postgres
# compiladas estáticamente — no requiere libpq-dev en el runtime stage.

# Stage 2: Final runtime
FROM python:3.12.10-slim

# Install Firefox and Chrome dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    firefox-esr \
    chromium \
    chromium-driver \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Geckodriver for Firefox
RUN wget -q https://github.com/mozilla/geckodriver/releases/download/v0.35.0/geckodriver-v0.35.0-linux64.tar.gz \
    && tar -xzf geckodriver-v0.35.0-linux64.tar.gz -C /usr/local/bin \
    && rm geckodriver-v0.35.0-linux64.tar.gz \
    && chmod +x /usr/local/bin/geckodriver

WORKDIR /app

# Copy dependencies from builder (includes psycopg2-binary)
COPY --from=builder /install /usr/local

# Copy application files
COPY . .

# Run scraper as default command
CMD ["python", "scraper.py"]
