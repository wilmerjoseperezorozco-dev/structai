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
# 2026-08-20: ultralytics ya no está en ningún requirements*.txt (no lo
# usa ningún código de apps/api, solo un script de entrenamiento local
# fuera del deploy — ver requirements.txt). Se deja este apt-get install
# de todas formas, sin condicionar a INSTALL_VISION/INSTALL_ESTRUCTURAL:
# es una capa de sistema barata (unos pocos MB) y quitarla sin poder
# probar el build localmente (sin Docker disponible en esta sesión)
# arriesgaba repetir el mismo fallo real ya documentado arriba por un
# ahorro marginal — no valía el riesgo.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ── Copiar todo el monorepo (contexto = raíz) para tener los packages/ disponibles ──
COPY . .

# ── Instalar dependencias de la API ──────────────────────────────
# 2026-08-20: requirements.txt ya NO trae torch/ifcopenshell/onnxruntime/
# opencv — se movieron a requirements-vision.txt y
# requirements-estructural.txt, instalados condicionalmente vía estos ARG.
# Default false en ambos porque coincide EXACTO con el estado real de
# producción hoy (ENABLE_YOLO=false, ENABLE_ESTRUCTURAL=false en las env
# vars del App Platform) — main.py nunca importa esos paquetes con los
# flags en false, así que no instalarlos no cambia el comportamiento
# actual, solo acelera el build y reduce el tamaño de la imagen.
#
# Para habilitar motor-estructural o YOLO en producción: (1) configurar
# el Build Argument correspondiente en DigitalOcean App Platform
# (Settings → App-Level → Build Arguments, o en el component si aplica),
# Y (2) configurar la env var de runtime (ENABLE_ESTRUCTURAL/ENABLE_YOLO)
# a "true" — los dos deben coincidir, si solo se activa la env var de
# runtime sin haber instalado el paquete, main.py lo captura con
# ImportError y el motor queda no disponible sin romper el resto de la
# API (no es peligroso olvidar el build arg, solo deja el motor apagado).
WORKDIR /app/apps/api
ARG INSTALL_VISION=false
ARG INSTALL_ESTRUCTURAL=false
RUN pip install --no-cache-dir -r requirements.txt \
    && if [ "$INSTALL_VISION" = "true" ]; then pip install --no-cache-dir -r requirements-vision.txt; fi \
    && if [ "$INSTALL_ESTRUCTURAL" = "true" ]; then pip install --no-cache-dir -r requirements-estructural.txt; fi

# ── Hornear el modelo de embeddings en la imagen ──────────────────
# rag_multi_norma.py fuerza HF_HUB_OFFLINE=1 en tiempo de ejecución
# (correcto: nunca debe depender de la red para responder /ask), pero
# eso asume que el modelo YA está en caché local — un contenedor nuevo
# nunca lo descargó. Causó "Error en RAG: couldn't connect to
# huggingface.co... and couldn't find them in the cached files" en el
# primer despliegue real. Se descarga aquí, en build time (con red
# disponible), para que quede horneado en la imagen y el contenedor en
# producción nunca necesite salir a internet por esto.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')"

# ── Variables de entorno (se pasan en runtime via --env-file) ────
ENV PORT=8000
ENV ENV=production
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# ── Arranque ──────────────────────────────────────────────────────
# 1 worker, no 2: cada worker carga por separado torch + ifcopenshell +
# opencv + scikit-learn + el modelo de embeddings — con 2 workers en una
# instancia de 1GB RAM, el proceso que atendía /ask moría (probable
# OOM-kill del kernel) justo después de cargar el modelo, y uvicorn lo
# reiniciaba en un ciclo que causaba 502/504 en cada consulta real.
# Confirmado en el log real de producción: "Waiting for child process
# [N]" → "Child process [N] died" → reinicio completo de la app,
# repetido en cada intento de /ask.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
