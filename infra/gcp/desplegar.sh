#!/usr/bin/env bash
# Construye, despliega y VERIFICA la API en Cloud Run. Uso: bash infra/gcp/desplegar.sh [--sin-pruebas]
# - Conserva las variables de entorno y secretos que ya tiene el servicio (no los toca).
# - La revisión nueva se despliega SIN tráfico; solo recibe tráfico si pasa la verificación.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; . "$HERE/config.sh"
RAIZ="$(cd "$HERE/../.." && pwd)"; cd "$RAIZ"
command -v gcloud >/dev/null || { echo "gcloud no está instalado o no está en el PATH"; exit 1; }

echo "[1/6] Árbol de trabajo"
if [ -n "$(git status --porcelain)" ]; then echo "Hay cambios sin confirmar: confirma antes de desplegar para que la imagen sea reproducible."; exit 1; fi
SHA="$(git rev-parse --short HEAD)"

if [ "${1:-}" != "--sin-pruebas" ]; then
  echo "[2/6] Pruebas locales previas"
  (cd apps/api && SUPABASE_URL=http://localhost:54321 SUPABASE_JWT_SECRET=local python -m pytest tests/test_router_proyecto.py tests/test_router_orquestador.py tests/test_router_analisis.py tests/test_router_concreto.py -q) || { echo "Pruebas fallidas: no se despliega."; exit 1; }
  (cd packages/dag-proyecto && python -m pytest tests -q) || { echo "Pruebas del DAG fallidas: no se despliega."; exit 1; }
fi

echo "[3/6] Imagen actual (para conservar el repositorio y poder revertir)"
descr() { gcloud run services describe "$SERVICIO" --region "$REGION" --project "$PROJECT" "$@"; }
ACTUAL="$(descr --format='value(spec.template.spec.containers[0].image)')"
[ -n "$ACTUAL" ] || { echo "No se pudo leer la imagen actual del servicio $SERVICIO"; exit 1; }
REPO="${ACTUAL%/*}"; IMAGEN="$REPO/structai-api:$SHA"
REV_ANTERIOR="$(descr --format='value(status.latestReadyRevisionName)')"
echo "  imagen actual: $ACTUAL"; echo "  imagen nueva:  $IMAGEN"; echo "  revisión anterior: $REV_ANTERIOR"

echo "[4/6] Construcción (Cloud Build)"
gcloud builds submit --project "$PROJECT" --config infra/gcp/cloudbuild.yaml --substitutions "_IMAGEN=$IMAGEN" .

echo "[5/6] Despliegue sin tráfico y verificación de la revisión candidata"
gcloud run deploy "$SERVICIO" --project "$PROJECT" --region "$REGION" --image "$IMAGEN" \
  --min-instances "$MIN_INSTANCIAS" --max-instances "$MAX_INSTANCIAS" --concurrency "$CONCURRENCIA" --timeout "$TIMEOUT" \
  --cpu-boost --no-traffic --tag candidata
URL_CAND="$(descr --format=json | python -c "import sys,json; t=[x for x in json.load(sys.stdin)['status']['traffic'] if x.get('tag')=='candidata']; print(t[0]['url'] if t else '')")"
[ -n "$URL_CAND" ] || { echo "No se obtuvo la URL de la revisión candidata"; exit 1; }
fallo=0
for ruta in /health /proyecto/salud /orquestador/salud /analisis/salud /concreto/salud; do
  code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 90 "$URL_CAND$ruta" || true)"
  echo "  $ruta -> ${code:-000}"; [ "${code:-000}" = "200" ] || fallo=1
done
if [ "$fallo" -ne 0 ]; then
  echo "X La revisión candidata NO pasó la verificación. El tráfico sigue en $REV_ANTERIOR."
  echo "  Logs: gcloud run services logs read $SERVICIO --region $REGION --project $PROJECT"
  exit 1
fi

echo "[6/6] Se mueve el tráfico a la revisión nueva"
gcloud run services update-traffic "$SERVICIO" --project "$PROJECT" --region "$REGION" --to-latest
URL="$(descr --format='value(status.url)')"
curl -s --max-time 60 "$URL/health?deep=true"; echo
echo "OK Desplegado $IMAGEN."
echo "Para revertir: gcloud run services update-traffic $SERVICIO --region $REGION --project $PROJECT --to-revisions $REV_ANTERIOR=100"
