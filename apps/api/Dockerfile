# ══════════════════════════════════════════════════════════════
# Construdata API — Dockerfile
# Build: docker build -t construdata-api .
# Run:   docker run -p 8000:8000 --env-file ../../.env construdata-api
# ══════════════════════════════════════════════════════════════

FROM python:3.11-slim

# Sistema: libGL para OpenCV headless
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ── Copiar todo el monorepo para tener los packages/ disponibles ──
COPY ../../ .

# ── Instalar dependencias de la API ──────────────────────────────
WORKDIR /app/apps/api
RUN pip install --no-cache-dir -r requirements.txt

# ── Variables de entorno (se pasan en runtime via --env-file) ────
ENV PORT=8000
ENV ENV=production
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# ── Arranque ──────────────────────────────────────────────────────
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
