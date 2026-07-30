# ══════════════════════════════════════════════════════════════
# Construdata API — Dockerfile
# El contexto de build DEBE ser la raíz del monorepo (no apps/api),
# porque el backend importa paquetes hermanos (packages/motor-*,
# packages/construdata) — COPY no puede salir del contexto de build
# con rutas "../..", así que este Dockerfile se invoca así:
#   docker build -f apps/api/Dockerfile -t construdata-api .   (desde la raíz)
# En DigitalOcean App Platform: source_dir "/" + dockerfile_path
# "apps/api/Dockerfile" logra lo mismo.
# Run: docker run -p 8000:8000 --env-file apps/api/.env construdata-api
# ══════════════════════════════════════════════════════════════

FROM python:3.11-slim

# Sistema: libGL real (paquete libgl1) — el comentario original decía
# "libGL para OpenCV" pero el paquete instalado era libglib2.0-0, que es
# una librería distinta (GLib, no OpenGL) y no trae libGL.so.1. Causó
# "motor-estructural no disponible: libGL.so.1: cannot open shared
# object file" en el primer despliegue real en DigitalOcean — ultralytics
# instala opencv-python (no solo -headless), que sí necesita libGL.so.1
# al importarse aunque no se use ninguna ventana/GUI.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ── Copiar todo el monorepo (contexto = raíz) para tener los packages/ disponibles ──
COPY . .

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
